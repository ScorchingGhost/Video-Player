$ErrorActionPreference = "Stop"

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$distributionDirectory = Join-Path $repositoryRoot "dist"
$buildDirectory = Join-Path $repositoryRoot "build\windows-app"
$appDirectory = Join-Path $distributionDirectory "LanguageVideoApp"
$archivePath = Join-Path $distributionDirectory "LanguageVideoApp-Windows.zip"
$venvPython = Join-Path $repositoryRoot ".venv\Scripts\python.exe"

if (Test-Path -LiteralPath $venvPython -PathType Leaf) {
    $pythonCommand = $venvPython
}
else {
    $pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
    if (-not $pythonLauncher) {
        throw "Python was not found. Install Python and the requirements in requirements-build.txt."
    }
    $pythonCommand = $pythonLauncher.Source
}

New-Item -ItemType Directory -Force -Path $distributionDirectory | Out-Null

Push-Location $PSScriptRoot
try {
    & $pythonCommand -m PyInstaller `
        --noconfirm `
        --clean `
        --onedir `
        --contents-directory "." `
        --name "LanguageVideoApp" `
        --distpath $distributionDirectory `
        --workpath $buildDirectory `
        --specpath $buildDirectory `
        --add-data "$PSScriptRoot\config.json;." `
        --add-data "$PSScriptRoot\index.php;." `
        --add-data "$PSScriptRoot\Media;Media" `
        --add-data "$PSScriptRoot\Script;Script" `
        --add-data "$PSScriptRoot\Style;Style" `
        "start.py"

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE."
    }

    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "Enable startup.cmd") -Destination $appDirectory
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "Disable startup.cmd") -Destination $appDirectory
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "Enable startup.ps1") -Destination $appDirectory
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "Disable startup.ps1") -Destination $appDirectory

    if (Test-Path -LiteralPath $archivePath) {
        Remove-Item -LiteralPath $archivePath
    }

    $tarCommand = Get-Command tar.exe -ErrorAction SilentlyContinue
    if (-not $tarCommand) {
        throw "Windows tar.exe was not found; cannot create the app archive."
    }
    & $tarCommand.Source -a -cf $archivePath -C $distributionDirectory "LanguageVideoApp"
    if ($LASTEXITCODE -ne 0) {
        throw "Creating the app archive failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

Write-Host "Windows app archive created: $archivePath"
