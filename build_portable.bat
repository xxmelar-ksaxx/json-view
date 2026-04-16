@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo Building Portable Release...
echo ==========================================

set "PORTABLE_DIR=json-view-portable-v0.1.0"
set "ZIP_FILE=json-view-portable-v0.1.0.zip"
set "SOURCE_EXE=dist\JSON View.exe"

:: Clean up old files
if exist "%PORTABLE_DIR%" rmdir /s /q "%PORTABLE_DIR%"
if exist "%ZIP_FILE%" del /f /q "%ZIP_FILE%"

:: Create new portable directory
mkdir "%PORTABLE_DIR%"

:: Check if the executable exists
if not exist "%SOURCE_EXE%" (
    echo Error: "%SOURCE_EXE%" not found!
    echo Please run build_windows.bat first.
    exit /b 1
)

:: Copy the executable and any potential runtime assets
echo Copying required files...
copy "%SOURCE_EXE%" "%PORTABLE_DIR%\" > nul

:: Create README.txt inside the portable folder
echo Creating README.txt...
(
echo JSON View - Portable Version
echo ============================
echo.
echo This is the portable version of JSON View.
echo.
echo How to run:
echo -----------
echo Simply double-click "JSON View.exe" to run the application.
echo.
echo Notes:
echo ------
echo - No installation is required.
echo - This version runs completely standalone in this folder.
echo - It does not add right-click context menu entries.
echo - It does not associate with .json files automatically.
echo - For system integration features, use the Windows installer version.
) > "%PORTABLE_DIR%\README.txt"

:: Create the zip archive
echo.
echo Creating ZIP archive ^(%ZIP_FILE%^)...
powershell -NoProfile -Command "Compress-Archive -Path '%PORTABLE_DIR%' -DestinationPath '%ZIP_FILE%' -Force"

echo.
echo Done! Portable build created safely:
echo - Directory: %PORTABLE_DIR%
echo - Archive:   %ZIP_FILE%
echo.
pause
