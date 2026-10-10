#!/bin/sh
base=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
"$base/run-python.sh" --check
result=$?
printf '\nPress Return to close.\n'
read answer
exit "$result"
