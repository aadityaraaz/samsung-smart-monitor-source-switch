"""Direct Samsung input switching through the official SmartThings CLI."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from uuid import UUID

ROOT = Path(__file__).resolve().parent
LABELS = ('HDMI 1', 'HDMI 2', 'USB-C')

def validate(config):
    try:
        UUID(config['device'])
    except (ValueError, KeyError, TypeError, AttributeError):
        raise ValueError('Set your monitor device UUID in config.json first.')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', config.get('component', '')):
        raise ValueError('Invalid component in config.json.')
    if config.get('capability') not in ('samsungvd.mediaInputSource', 'mediaInputSource'):
        raise ValueError('Use a supported mediaInputSource capability.')
    for label in LABELS:
        value = config.get('mapping', {}).get(label)
        if not isinstance(value, str) or not value:
            raise ValueError('Configure an input ID for ' + label)
    return config

def command(config, source):
    validate(config)
    if source not in LABELS:
        raise ValueError('Unknown source label.')
    return ['devices:commands', config['device'],
        config['component'] + ':' + config['capability'] + ':setInputSource(' +
        json.dumps(config['mapping'][source]) + ')']

def cli_path(config):
    explicit = config.get('cli', '')
    if explicit:
        if not Path(explicit).is_absolute() or not Path(explicit).is_file():
            raise ValueError('The configured CLI must be an existing absolute file path.')
        return explicit
    for path in (ROOT / 'bin/smartthings', Path('/opt/homebrew/bin/smartthings'),
                 Path('/usr/local/bin/smartthings')):
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
    path = shutil.which('smartthings')
    if path:
        return path
    raise RuntimeError('Install the official SmartThings CLI; see README.md.')

def cli(config, args):
    env = os.environ.copy()
    env.pop('SMARTTHINGS_DEBUG', None)
    env.pop('SMARTTHINGS_PROFILE', None)
    with (ROOT / '.cli.lock').open('a') as guard:
        fcntl.flock(guard, fcntl.LOCK_EX)
        result = subprocess.run([cli_path(config), *args], capture_output=True,
            text=True, timeout=660, env=env)
    if result.returncode:
        raise RuntimeError('Samsung CLI failed. Run Connect Samsung.command to reauthenticate and check API access.')
    return result.stdout

def input_ids(attrs):
    values = set()
    for key in ('supportedInputSources', 'supportedInputSourcesMap'):
        value = attrs.get(key, {}).get('value', [])
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except ValueError:
                continue
        if isinstance(value, list):
            for item in value:
                candidate = item.get('id') if isinstance(item, dict) else item
                if isinstance(candidate, str):
                    values.add(candidate)
    return values

def check(config):
    validate(config)
    device = json.loads(cli(config, ['devices', config['device'], '--json']))
    component = next((c for c in device.get('components', [])
        if c.get('id') == config['component']), None)
    if not component or not any(c.get('id') == config['capability']
        for c in component.get('capabilities', [])):
        raise ValueError('The configured component/capability is not reported by this monitor.')
    status = json.loads(cli(config, ['devices:status', config['device'], '--json']))
    attrs = status.get('components', {}).get(config['component'], {}).get(config['capability'], {})
    supported = input_ids(attrs)
    if not supported:
        raise ValueError('Monitor did not report its supported inputs. Inspect devices:status before configuring.')
    if not set(config['mapping'].values()).issubset(supported):
        raise ValueError('Configured source IDs do not match the monitor. Inspect devices:status --json.')
    return 'Samsung login and input mappings verified. No input was changed.'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', nargs='?', choices=LABELS)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'config.json'
    if not path.is_file():
        raise ValueError('Copy config.example.json to config.json and fill in your monitor settings.')
    config = json.loads(path.read_text())
    if args.check:
        print(check(config))
    elif args.source:
        argv = command(config, args.source)
        if args.dry_run:
            print(json.dumps(argv))
        else:
            cli(config, argv)
            print(args.source + ': command accepted by Samsung. Confirm the physical input.')
    else:
        parser.error('Choose a source or --check.')

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('M7 Source Switch: ' + str(error), file=sys.stderr)
        sys.exit(1)
