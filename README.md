# M7 Source Switch

Direct **HDMI 1**, **HDMI 2**, and **USB-C** input buttons for Samsung M7 smart monitors, with optional Logitech Actions Ring integration on macOS and Windows.

The launchers send an input command through SmartThings. They do not open the monitor's source menu or simulate remote-control navigation. No web server needs to stay running.

This is an independent community project, not an official Samsung or Logitech product.

<img width="523" height="431" alt="Screen Shot 2026-10-10 at 13 47 08 PM" src="https://github.com/user-attachments/assets/ea4b95d9-5c2f-42ae-b39b-7e062ef4c56e" />


## What is included

| Platform | Buttons | Supporting files |
| --- | --- | --- |
| macOS | `M7 HDMI 1.app`, `M7 HDMI 2.app`, `M7 USB-C.app` | Installer, Python controller, login/check launcher, example configuration |
| Windows | Three `.cmd` buttons and three silent `.vbs` buttons | Shared command helper and example configuration |

```text
macos/
  Install.command
  Connect Samsung.command
  config.example.json
  trigger.py
  run-python.sh
  M7 HDMI 1.app/
  M7 HDMI 2.app/
  M7 USB-C.app/
windows/
  config.cmd.example
  switch.cmd
  M7 HDMI 1.cmd / M7 HDMI 1.vbs
  M7 HDMI 2.cmd / M7 HDMI 2.vbs
  M7 USB-C.cmd / M7 USB-C.vbs
tests/
LICENSE
.gitignore
```

Vendor installers, CLI binaries, personal monitor settings, and authentication credentials are not included.

## Requirements

- A monitor added to your Samsung SmartThings account and online.
- SmartThings must expose an input-selection capability for that monitor. This is model/firmware dependent; the project was developed with a Samsung M7 LS43BM702.
- Internet access on the computer and monitor. This uses Samsung's cloud API, not a local Wi-Fi remote protocol.
- Samsung's official [SmartThings CLI](https://developer.smartthings.com/docs/sdks/cli), installed separately for each computer.
- macOS: Python 3.8 or newer. No third-party Python packages are needed. Homebrew Python or the Apple Command Line Tools Python can be used.
- Windows: Command Prompt. Silent launchers additionally require Windows Script Host with VBScript available. They do not require Python or Node.
- For Actions Ring: Logi Options+ and compatible Logitech hardware. Switching both input devices requires both to be paired to the destination computer.

Samsung login uses the CLI's browser-based OAuth flow. The CLI manages token renewal; login can be required again if renewal fails or access is revoked. This project does not guarantee permanent authorization or bypass Samsung API account, subscription, or rate-limit requirements.

## 1. Install the official SmartThings CLI

### macOS

With Homebrew:

```sh
brew install smartthingscommunity/smartthings/smartthings
smartthings --version
```

Alternatively, download the appropriate Mac binary for your CPU from the [official releases](https://github.com/SmartThingsCommunity/smartthings-cli/releases/latest). Install it on your PATH or use its absolute path in the Mac configuration. The launcher also checks the standard Homebrew paths.

### Windows

Download and install **smartthings.msi** from the [official releases](https://github.com/SmartThingsCommunity/smartthings-cli/releases/latest).

Open PowerShell and check the installation:

```powershell
where.exe smartthings.exe
& 'C:\Program Files\SmartThings\smartthings.exe' --version
```

If your installation is elsewhere, use the path printed by `where.exe` in the commands below. The `.msi` is an installer, not the executable.

Restart Logi Options+ after installing the CLI. The Windows helper checks the standard installation path even if Logitech has an outdated PATH.

## 2. Sign in and discover your monitor

Run this on each computer, and complete Samsung's browser sign-in:

```sh
smartthings devices --json
```

On Windows, a full executable path works even when PATH is unavailable:

```powershell
& 'C:\Program Files\SmartThings\smartthings.exe' devices --json
```

Find your monitor in the output and copy its **deviceId**. Use that ID to inspect its capabilities and current status:

```sh
smartthings devices YOUR_DEVICE_ID --json
smartthings devices:status YOUR_DEVICE_ID --json
```

For Windows, prepend the full CLI path as in the previous example.

In device details, find the component containing `samsungvd.mediaInputSource` or `mediaInputSource`. In status, inspect that capability's `supportedInputSources` or `supportedInputSourcesMap`. Use the exact input **IDs**, including letter case, rather than friendly names.

The example settings assume:

| Button | Example input ID |
| --- | --- |
| HDMI 1 | `HDMI1` |
| HDMI 2 | `HDMI2` |
| USB-C | `USB-C` |

These values matched the original M7 setup. Verify your own monitor before using them. If neither capability is reported, these launchers cannot provide direct switching for that device.

Your Samsung login on one computer is not copied to another. Authenticate separately on the Mac and Windows PC.

## 3A. Set up macOS buttons

1. Download/extract this project or clone it locally.
2. Run `macos/Install.command`. It copies the launchers and controller into:

   ```text
   ~/Library/Application Support/M7SourceSwitch/
   ```

   If executable permissions were lost during download, run this in the project directory first:

   ```sh
   chmod +x macos/*.command macos/run-python.sh macos/*.app/Contents/MacOS/invoke
   ```

3. Edit **config.json in the installed folder**, not `config.example.json` in the repository. Fill in your device ID, component, capability, and input IDs:

   ```json
   {
     "device": "YOUR_SMARTTHINGS_DEVICE_ID",
     "component": "main",
     "capability": "samsungvd.mediaInputSource",
     "mapping": {
       "HDMI 1": "HDMI1",
       "HDMI 2": "HDMI2",
       "USB-C": "USB-C"
     },
     "cli": ""
   }
   ```

   Leave `cli` empty for automatic discovery, or set it to an existing absolute CLI executable path. The monitor ID and mappings remain local.

4. Run the installed **Connect Samsung.command**. It checks login, the capability, and the reported input IDs without changing the input.
5. Open each installed `.app` to test the corresponding source. Keep the entire installed folder intact.

The Application Support location avoids the Documents access error encountered when Logitech started the original scripts. These apps are simple unsigned script bundles, not notarized installers. Review the source and follow your organization's software policy. This package does not disable macOS security protections.

To inspect the command without sending it:

```sh
"$HOME/Library/Application Support/M7SourceSwitch/run-python.sh" 'HDMI 1' --dry-run
```

## 3B. Set up Windows buttons

1. Copy the **entire windows folder** to a permanent local location, for example `C:\Monitor`. Keep the helper and buttons together.
2. Copy `config.cmd.example` to **config.cmd**. Open the new file in Notepad and replace the placeholder device ID and any mappings that differ:

   ```cmd
   set "M7_DEVICE_ID=YOUR_SMARTTHINGS_DEVICE_ID"
   set "M7_COMPONENT=main"
   set "M7_CAPABILITY=samsungvd.mediaInputSource"
   set "M7_HDMI1=HDMI1"
   set "M7_HDMI2=HDMI2"
   set "M7_USBC=USB-C"
   set "M7_CLI_PATH="
   ```

   The configuration is a local batch script; edit only trusted values. The input IDs should be simple strings like those above.

3. If your CLI is installed in a custom location, set its absolute path:

   ```cmd
   set "M7_CLI_PATH=C:\Program Files\SmartThings\smartthings.exe"
   ```

   Discovery order is: configured path, adjacent `smartthings.exe`, standard Program Files path, then PATH. An explicitly configured but incorrect path produces an error.

4. Double-click **M7 USB-C.cmd** for the first test. Complete Samsung sign-in if prompted. This changes the input; test HDMI 1 and HDMI 2 as well.
5. Once visible command launchers work, use the corresponding **.vbs** files for silent launches. They open the `.cmd` files with a hidden command window. Keep each `.vbs` filename paired with its `.cmd` filename.

If VBScript is unavailable or blocked on your Windows installation, use the visible `.cmd` buttons. The project does not enable scripting features or bypass organizational restrictions automatically.

## 4. Assign Logitech Actions Ring buttons

Set this up in Logi Options+ on **each computer** from which you want to switch.

1. Open Actions Ring customization and select the global/all-applications profile.
2. Create a **Monitor** folder, or use three available ring slots.
3. Drag **Open File** into a slot. This allows selection of the generated launcher even when Open Application only lists installed applications.
4. Set the file path to the matching installed Mac `.app` or Windows `.vbs` file. Label it HDMI 1, HDMI 2, or USB-C.
5. Repeat for the other inputs and test from the actual ring.

Example Windows paths:

```text
C:\Monitor\M7 HDMI 1.vbs
C:\Monitor\M7 HDMI 2.vbs
C:\Monitor\M7 USB-C.vbs
```

Example Mac path (replace YOUR_USER):

```text
/Users/YOUR_USER/Library/Application Support/M7SourceSwitch/M7 HDMI 1.app
```

### Optional: switch mouse and keyboard with the monitor

The source files only switch **video input**. Device switching is configured separately inside Logitech, using a **Multi-action (macro)** for each destination:

1. **Open File**: run the matching source launcher.
2. **Delay**: start with 3000 ms and adjust after testing.
3. **Easy-Switch 2 Devices**: choose your mouse and keyboard, and select the destination computer for each.

Example mapping:

| Monitor input | Destination | Mouse channel | Keyboard channel |
| --- | --- | --- | --- |
| HDMI 1 | Personal PC | Your pairing | Your pairing |
| HDMI 2 | Work PC | Your pairing | Your pairing |
| USB-C | MacBook | Your pairing | Your pairing |

Both devices must already be paired to each destination. Channel numbers do not have to match between mouse and keyboard, but each selection must point to the same intended computer.

Configure a return action on the destination computer too. Test one destination first before replacing all existing actions.

The delay is a timing aid, not a success check: Logitech may switch the peripherals even if Samsung rejects the monitor command. The launchers log the result, but a macro does not read that result. A reported accepted command also does not prove the physical display changed.

Logitech documents [Easy-Switch for two or three devices in Actions Ring](https://support.logi.com/hc/en-001/articles/34377296585111-How-can-I-set-up-Easy-Switch-in-Actions-Ring). Options+ integration is for Windows and macOS; this package does not provide Linux Actions Ring integration.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Works by double-click but Logitech cannot find the CLI | Set the absolute CLI path in configuration; restart Options+ after installation. |
| PowerShell `where smartthings.exe` prints nothing | Use **where.exe**, because PowerShell's `where` is an alias. |
| Windows command window flashes | Point Logitech at the matching `.vbs`, not `.cmd`. Confirm Windows Script Host/VBScript is available. |
| Silent Windows button appears to do nothing | Try the `.cmd` visibly and inspect logs. Sign in visibly before using silent buttons. |
| macOS reports Operation not permitted for a script in Documents | Use Install.command and assign apps from Application Support. |
| Python missing or developer tools prompt | Install Python 3 before using the Mac apps. The launcher checks Homebrew paths before Apple's Python. |
| Unsupported or wrong input | Inspect device details/status and use exact source IDs. |
| Samsung login/API failure | Re-run CLI sign-in visibly, check monitor connectivity and your account's API access. |
| Monitor switches but peripherals stay on the old computer | Add/configure the Easy-Switch step in Logitech and verify both devices' pairings. |

Logs:

- Mac: `~/Library/Application Support/M7SourceSwitch/hdmi1.log`, `hdmi2.log`, `usbc.log`.
- Windows: `%LOCALAPPDATA%\M7SourceSwitch\hdmi1.log`, `hdmi2.log`, `usbc.log`, or `error.log` for setup errors.

Avoid rapidly clicking multiple destinations while login or token renewal is in progress. Mac CLI calls are serialized; Windows launchers do not serialize simultaneous requests.

## Public GitHub upload

Create a repository, then upload **the contents of this public project folder**. Do not upload the earlier personal prototype or the installed runtime folders.

This folder includes example settings and excludes live configuration, logs, CLI binaries, and tokens. `.gitignore` helps keep those files out of future commits, but it does not remove files already tracked by Git. Review staged files before pushing.

For a local repository, from this folder:

```sh
git init
git add .
git status --short
git commit -m "Add Mac and Windows Samsung M7 source launchers"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

A new computer must install its own CLI, sign in, and create local configuration. Never commit the CLI's OAuth storage, a personal access token, or a filled-in configuration file.

## Validation and limitations

The original Mac launcher was verified with a real M7, including USB-C switching from Actions Ring. The original Windows command buttons were reported working by the user. This public version generalizes the configuration and has automated command/mapping checks; it still needs a live setup test on each user's computers. Silent VBS launchers and the full three-destination peripheral macros have not been confirmed end-to-end in this development environment.

Run local Mac controller/package checks:

```sh
python3 -m unittest discover -s tests -v
```

Windows batch smoke checks can be run in PowerShell without contacting Samsung:

```powershell
powershell -NoProfile -File .\tests\test-windows.ps1
```

If your execution policy does not permit local scripts, use an approved development environment or the included GitHub Actions workflow. No policy changes are required by this project.

## License

Project code is licensed under [MIT](LICENSE). Samsung's CLI is installed independently and remains subject to its own license and service terms. Samsung, SmartThings, and Logitech names belong to their respective owners.
