@echo off
REM ============================================
REM  Uninstall JSON View from Windows
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

echo.
echo Uninstalling JSON View...
echo.

:: Remove application registration
echo [1/4] Removing application registration...
reg delete "HKLM\SOFTWARE\Classes\Applications\JSON View.exe" /f >nul 2>&1

:: Remove file type registration
echo [2/4] Removing file type registration...
reg delete "HKLM\SOFTWARE\Classes\JSONView.JsonFile" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\.json" /v "" /f >nul 2>&1

:: Remove .json context menu
echo [3/4] Removing .json context menu...
reg delete "HKLM\SOFTWARE\Classes\SystemFileAssociations\.json\shell\OpenWithJSONView" /f >nul 2>&1

:: Remove general context menu
echo [4/4] Removing general context menu...
reg delete "HKLM\SOFTWARE\Classes\*\shell\OpenWithJSONView" /f >nul 2>&1

echo.
echo ============================================
echo   Uninstallation complete!
echo   JSON View has been removed from the system.
echo ============================================
pause
