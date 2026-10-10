@echo off
setlocal
set "SMARTTHINGS_DEBUG="
set "SMARTTHINGS_PROFILE="
set "m7_data=%LOCALAPPDATA%\M7SourceSwitch"
if not exist "%m7_data%" mkdir "%m7_data%"
set "m7_log=%m7_data%\error.log"
if not exist "%~dp0config.cmd" (
  > "%m7_log%" echo Copy config.cmd.example to config.cmd and configure your monitor first.
  goto failed
)
call "%~dp0config.cmd"
if not defined M7_DEVICE_ID goto badconfig
if "%M7_DEVICE_ID%"=="YOUR_SMARTTHINGS_DEVICE_ID" goto badconfig
if not defined M7_COMPONENT goto badconfig
if not defined M7_CAPABILITY goto badconfig
set "m7_input="
if "%~1"=="HDMI 1" set "m7_input=%M7_HDMI1%"
if "%~1"=="HDMI 1" set "m7_log=%m7_data%\hdmi1.log"
if "%~1"=="HDMI 2" set "m7_input=%M7_HDMI2%"
if "%~1"=="HDMI 2" set "m7_log=%m7_data%\hdmi2.log"
if "%~1"=="USB-C" set "m7_input=%M7_USBC%"
if "%~1"=="USB-C" set "m7_log=%m7_data%\usbc.log"
if not defined m7_input goto badconfig
set "m7_cli=%M7_CLI_PATH%"
if defined m7_cli goto validatecli
if exist "%~dp0smartthings.exe" set "m7_cli=%~dp0smartthings.exe"
if defined m7_cli goto validatecli
if exist "%ProgramFiles%\SmartThings\smartthings.exe" set "m7_cli=%ProgramFiles%\SmartThings\smartthings.exe"
if defined m7_cli goto validatecli
for /f "delims=" %%I in ('where smartthings.exe 2^>nul') do set "m7_cli=%%I"
:validatecli
if not defined m7_cli goto missingcli
if not exist "%m7_cli%" goto missingcli
set "m7_request=%m7_data%\request-%RANDOM%-%RANDOM%.json"
> "%m7_request%" echo {"component":"%M7_COMPONENT%","capability":"%M7_CAPABILITY%","command":"setInputSource","arguments":["%m7_input%"]}
call "%m7_cli%" devices:commands "%M7_DEVICE_ID%" --input "%m7_request%" > "%m7_log%" 2>&1
set "m7_result=%ERRORLEVEL%"
del "%m7_request%" >nul 2>&1
if not "%m7_result%"=="0" goto failed
exit /b 0
:badconfig
> "%m7_log%" echo Invalid configuration. Fill in your monitor UUID and all source settings in config.cmd.
goto failed
:missingcli
> "%m7_log%" echo SmartThings CLI not found. Install Samsung's CLI or set M7_CLI_PATH in config.cmd.
:failed
type "%m7_log%"
echo See README.md. Use a visible .cmd launcher to troubleshoot Samsung login.
pause
exit /b 1
