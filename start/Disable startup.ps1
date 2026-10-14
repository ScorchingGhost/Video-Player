$ErrorActionPreference = "Stop"

$shortcutPath = Join-Path ([Environment]::GetFolderPath("Startup")) "Language Video App.lnk"
if (Test-Path -LiteralPath $shortcutPath) {
    Remove-Item -LiteralPath $shortcutPath
    Write-Host "The app has been removed from Windows startup."
}
else {
    Write-Host "The app is not currently set to start with Windows."
}
