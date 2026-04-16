@echo off
echo ============================================
echo   Building JSON View for Windows
echo ============================================
echo.

REM Check Python
python --version 2>NUL
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install pyinstaller Pillow

REM Create icon
echo.
echo Creating icon files...
python create_icon.py

REM Build with PyInstaller
echo.
echo Building executable...
pyinstaller --onefile ^
    --windowed ^
    --name "JSON View" ^
    --icon icon.ico ^
    --add-data "icon.ico;." ^
    --add-data "icon.png;." ^
    json_view.py

echo.
echo ============================================
echo   Build complete!
echo   Output: dist\JSON View.exe
echo ============================================
pause
