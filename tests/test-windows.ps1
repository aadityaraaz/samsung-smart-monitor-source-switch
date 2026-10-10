$ErrorActionPreference = 'Stop'
$project = Split-Path $PSScriptRoot -Parent
$temp = Join-Path ([IO.Path]::GetTempPath()) ('M7 test ' + [guid]::NewGuid())
$oldData = $env:LOCALAPPDATA
try {
    New-Item -ItemType Directory -Path $temp | Out-Null
    $buttons = Join-Path $temp 'buttons with spaces'
    Copy-Item (Join-Path $project 'windows') $buttons -Recurse
    $env:LOCALAPPDATA = Join-Path $temp 'data'
    $fake = Join-Path $buttons 'fake-cli.cmd'
    @'
@echo off
if not "%~1"=="devices:commands" exit /b 2
if not "%~2"=="00000000-0000-4000-8000-000000000001" exit /b 3
if not "%~3"=="--input" exit /b 4
type "%~4"
exit /b 0
'@ | Set-Content -Encoding ASCII $fake
    $configuration = Get-Content (Join-Path $buttons 'config.cmd.example') -Raw
    $configuration = $configuration.Replace('YOUR_SMARTTHINGS_DEVICE_ID', '00000000-0000-4000-8000-000000000001')
    $configuration = $configuration.Replace('set "M7_CLI_PATH="', ('set "M7_CLI_PATH=' + $fake + '"'))
    $configuration | Set-Content -Encoding ASCII (Join-Path $buttons 'config.cmd')
    foreach ($item in @(@('HDMI 1','HDMI1','hdmi1'), @('HDMI 2','HDMI2','hdmi2'), @('USB-C','USB-C','usbc'))) {
        $button = Join-Path $buttons ('M7 ' + $item[0] + '.cmd')
        & $button
        if ($LASTEXITCODE -ne 0) { throw "Batch launcher failed: $button" }
        $log = Join-Path $env:LOCALAPPDATA ('M7SourceSwitch\' + $item[2] + '.log')
        $request = Get-Content $log -Raw | ConvertFrom-Json
        if ($request.arguments[0] -ne $item[1] -or $request.command -ne 'setInputSource' -or $request.capability -ne 'samsungvd.mediaInputSource') {
            throw ('Incorrect request for ' + $item[0])
        }
        Write-Output ('PASS: ' + $item[0] + ' request and executable path with spaces')
    }
    if (Get-ChildItem (Join-Path $env:LOCALAPPDATA 'M7SourceSwitch') -Filter 'request-*.json') {
        throw 'Temporary request files were not cleaned up.'
    }
} finally {
    $env:LOCALAPPDATA = $oldData
    if (Test-Path $temp) { Remove-Item $temp -Recurse -Force }
}
