# Language Video App

Windows kiosk app that displays language buttons and plays the configured videos.

## Download and run

Download and extract `LanguageVideoApp-Windows.zip`, then run
`LanguageVideoApp.exe` from the extracted `LanguageVideoApp` folder. Keep the
whole folder together; the app includes its videos, images, and configuration.
Python is not required on the target PC. Microsoft Edge must be installed.

To launch the app automatically when your Windows account signs in, run
`Enable startup.cmd` from the extracted folder. Run `Disable startup.cmd` to
remove that shortcut. Leave the app folder in the same location after enabling
startup.

Edit `config.json` in the extracted folder to change the button labels or
videos. Video paths are relative to the app folder by default.

## Build the Windows download

From the repository root, install the build requirements and create the ZIP.
If the repository has a `.venv` folder, use its interpreter; otherwise use the
Python launcher:

```powershell
if (Test-Path .\.venv\Scripts\python.exe) {
    .\.venv\Scripts\python.exe -m pip install -r .\requirements-build.txt
} else {
    py -m pip install -r .\requirements-build.txt
}
powershell -ExecutionPolicy Bypass -File .\start\build_windows.ps1
```

The finished archive is written to `dist\LanguageVideoApp-Windows.zip`. It
contains the app and its runtime assets, including the media files.