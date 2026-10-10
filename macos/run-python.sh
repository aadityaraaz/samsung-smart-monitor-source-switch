#!/bin/sh
set -eu
base=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
for m7_python in /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3; do
  if [ -x "$m7_python" ]; then
    exec "$m7_python" "$base/trigger.py" "$@"
  fi
done
printf 'Python 3 is required. See README.md.\n' >&2
exit 1
