$ErrorActionPreference = "Stop"

$application = Join-Path $PSScriptRoot "LanguageVideoApp.exe"
if (-not (Test-Path -LiteralPath $application -PathType Leaf)) {
    throw "LanguageVideoApp.exe was not found. Run this file from the extracted app folder."
}

$startupDirectory = [Environment]::GetFolderPath("Startup")
$shortcutPath = Join-Path $startupDirectory "Language Video App.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $application
$shortcut.WorkingDirectory = $PSScriptRoot
$shortcut.Description = "Start the Language Video App when Windows signs in."
$shortcut.Save()

Write-Host "The app will open when this Windows account signs in."
