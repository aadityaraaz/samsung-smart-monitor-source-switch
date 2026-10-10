import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if os.name == 'posix':
    spec = importlib.util.spec_from_file_location('m7_trigger', ROOT / 'macos/trigger.py')
    trigger = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trigger)

DEVICE = '00000000-0000-4000-8000-000000000001'

@unittest.skipUnless(os.name == 'posix', 'Mac controller uses POSIX locking')
class ControllerTests(unittest.TestCase):
    def config(self):
        return dict(device=DEVICE, component='main', capability='samsungvd.mediaInputSource',
            mapping={'HDMI 1':'HDMI1', 'HDMI 2':'HDMI2', 'USB-C':'USB-C'})

    def test_all_three_commands_preserve_source_ids(self):
        config = self.config()
        for label, source in config['mapping'].items():
            self.assertEqual(trigger.command(config, label), ['devices:commands', DEVICE,
                'main:samsungvd.mediaInputSource:setInputSource(' + json.dumps(source) + ')'])

    def test_invalid_config_and_unknown_source_do_not_send(self):
        config = self.config()
        config['device'] = 'YOUR_SMARTTHINGS_DEVICE_ID'
        with self.assertRaises(ValueError): trigger.command(config, 'HDMI 1')
        config = self.config()
        config['capability'] = 'switch'
        with self.assertRaises(ValueError): trigger.command(config, 'HDMI 1')
        with self.assertRaises(ValueError): trigger.command(self.config(), 'Other')

    def test_check_requires_reported_sources_and_never_sends(self):
        config = self.config()
        device = {'components':[{'id':'main','capabilities':[{'id':config['capability']}]}]}
        status = {'components':{'main':{config['capability']:{'supportedInputSourcesMap':{
            'value':[{'id':v, 'name':k} for k,v in config['mapping'].items()]}}}}}
        with patch.object(trigger, 'cli', side_effect=[json.dumps(device), json.dumps(status)]) as call:
            self.assertIn('verified', trigger.check(config))
            self.assertEqual([c.args[1][0] for c in call.call_args_list], ['devices','devices:status'])
        status['components']['main'][config['capability']]['supportedInputSourcesMap']['value'] = ['HDMI1']
        with patch.object(trigger, 'cli', side_effect=[json.dumps(device), json.dumps(status)]):
            with self.assertRaises(ValueError): trigger.check(config)

    def test_cli_preserves_arguments_and_suppresses_vendor_error_output(self):
        with tempfile.TemporaryDirectory(prefix='M7 test ') as folder:
            base = Path(folder)
            fake = base / 'fake cli'
            fake.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
            fake.chmod(0o755)
            config = self.config(); config['cli'] = str(fake)
            argv = trigger.command(config, 'USB-C')
            with patch.object(trigger, 'ROOT', base):
                self.assertEqual(trigger.cli(config, argv).splitlines(), argv)
                fake.write_text('#!/bin/sh\necho private-token-example >&2\nexit 1\n')
                with self.assertRaises(RuntimeError) as failure: trigger.cli(config, argv)
                self.assertNotIn('private-token-example', str(failure.exception))

class PackageTests(unittest.TestCase):
    def test_windows_wrappers_use_relative_paths_and_hidden_mode(self):
        for label in ('HDMI 1','HDMI 2','USB-C'):
            batch = (ROOT/'windows'/f'M7 {label}.cmd').read_text()
            self.assertIn('"%~dp0switch.cmd" "'+label+'"', batch)
            vbs = (ROOT/'windows'/f'M7 {label}.vbs').read_text()
            self.assertIn('WScript.ScriptFullName',vbs)
            self.assertIn(', 0, False',vbs)
        helper = (ROOT/'windows/switch.cmd').read_text()
        self.assertIn('%ProgramFiles%\\SmartThings\\smartthings.exe', helper)

    def test_release_contains_no_live_configuration(self):
        self.assertFalse((ROOT/'macos/config.json').exists())
        self.assertFalse((ROOT/'windows/config.cmd').exists())
        for path in ROOT.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                self.assertNotEqual(path.suffix,'.log')

if __name__ == '__main__': unittest.main()
