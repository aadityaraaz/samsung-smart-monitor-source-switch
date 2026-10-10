#!/bin/sh
set -eu
source_dir=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
install_dir="$HOME/Library/Application Support/M7SourceSwitch"
mkdir -p "$install_dir"
if [ "$source_dir" != "$install_dir" ]; then
  for item in "M7 HDMI 1.app" "M7 HDMI 2.app" "M7 USB-C.app" trigger.py run-python.sh config.example.json "Connect Samsung.command"; do
    cp -R "$source_dir/$item" "$install_dir/"
  done
fi
if [ ! -f "$install_dir/config.json" ]; then
  cp "$install_dir/config.example.json" "$install_dir/config.json"
fi
printf 'Installed in: %s\n' "$install_dir"
printf 'Edit config.json there, then run Connect Samsung.command.\nExisting configuration was preserved.\nPress Return to close.\n'
read answer
