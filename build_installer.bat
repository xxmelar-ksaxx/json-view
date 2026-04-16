@echo off
echo ============================================
echo   Building JSON View Installer
echo ============================================
echo.

:: Standard default path to Inno Setup command line compiler
set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if not exist "%ISCC%" (
    echo ERROR: Inno Setup 6 not found at "%ISCC%".
    echo Please install it from https://jrsoftware.org/isinfo.php
    pause
    exit /b 1
)

if not exist "dist\JSON View.exe" (
    echo ERROR: 'dist\JSON View.exe' not found.
    echo Please run build_windows.bat first.
    pause
    exit /b 1
)

echo Compiling installer.iss...
"%ISCC%" installer.iss

if errorlevel 1 (
    echo ERROR: Failed to build the installer.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Installer Build Complete!
echo   Outputs to: dist\json-view-setup-v0.1.0.exe
echo ============================================
pause
