@echo off
REM ============================================
REM  Install JSON View into Windows Right-Click
REM  Context Menu & Set as Default JSON Opener
REM  !! Run as Administrator !!
REM ============================================

:: Check for admin privileges
net session >nul 2>&1
if errorlevel 1 (
    echo This script requires Administrator privileges.
    echo Right-click and select "Run as administrator".
    pause
    exit /b 1
)

:: Detect the EXE path
set "EXE_PATH=%~dp0dist\JSON View.exe"

if not exist "%EXE_PATH%" (
    echo ERROR: "JSON View.exe" not found at:
    echo   %EXE_PATH%
    echo.
    echo Please build the application first using build_windows.bat
    pause
    exit /b 1
)

echo.
echo Installing JSON View...
echo EXE: %EXE_PATH%
echo.

:: ── 1. Register the application ──
echo [1/4] Registering application...
reg add "HKLM\SOFTWARE\Classes\Applications\JSON View.exe" /ve /d "JSON View" /f >nul
reg add "HKLM\SOFTWARE\Classes\Applications\JSON View.exe\shell\open\command" /ve /d "\"%EXE_PATH%\" \"%%1\"" /f >nul

:: ── 2. Register file type ──
echo [2/4] Registering .json file type...
reg add "HKLM\SOFTWARE\Classes\.json" /ve /d "JSONView.JsonFile" /f >nul
reg add "HKLM\SOFTWARE\Classes\JSONView.JsonFile" /ve /d "JSON File" /f >nul
reg add "HKLM\SOFTWARE\Classes\JSONView.JsonFile\DefaultIcon" /ve /d "\"%EXE_PATH%\",0" /f >nul
reg add "HKLM\SOFTWARE\Classes\JSONView.JsonFile\shell\open" /ve /d "Open with JSON View" /f >nul
reg add "HKLM\SOFTWARE\Classes\JSONView.JsonFile\shell\open\command" /ve /d "\"%EXE_PATH%\" \"%%1\"" /f >nul

:: ── 3. Add to right-click context menu for .json files ──
echo [3/4] Adding right-click context menu...
reg add "HKLM\SOFTWARE\Classes\SystemFileAssociations\.json\shell\OpenWithJSONView" /ve /d "Open with JSON View" /f >nul
reg add "HKLM\SOFTWARE\Classes\SystemFileAssociations\.json\shell\OpenWithJSONView" /v "Icon" /d "\"%EXE_PATH%\",0" /f >nul
reg add "HKLM\SOFTWARE\Classes\SystemFileAssociations\.json\shell\OpenWithJSONView\command" /ve /d "\"%EXE_PATH%\" \"%%1\"" /f >nul

:: ── 4. Add general right-click "Open with JSON View" for all files ──
echo [4/4] Adding general context menu option...
reg add "HKLM\SOFTWARE\Classes\*\shell\OpenWithJSONView" /ve /d "Open with JSON View" /f >nul
reg add "HKLM\SOFTWARE\Classes\*\shell\OpenWithJSONView" /v "Icon" /d "\"%EXE_PATH%\",0" /f >nul
reg add "HKLM\SOFTWARE\Classes\*\shell\OpenWithJSONView\command" /ve /d "\"%EXE_PATH%\" \"%%1\"" /f >nul

echo.
echo ============================================
echo   Installation complete!
echo.
echo   - JSON View is now the default .json opener
echo   - Right-click any .json file to see "Open with JSON View"
echo   - Right-click any file to see "Open with JSON View"
echo ============================================
pause
