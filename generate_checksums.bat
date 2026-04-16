@echo off
setlocal enabledelayedexpansion

set CHECKSUMS_FILE=checksums.txt
if exist "%CHECKSUMS_FILE%" del "%CHECKSUMS_FILE%"

set FILES_FOUND=0

for %%F in (json-view-windows-setup-*.exe json-view-windows-portable-*.zip) do (
    if exist "%%F" (
        set FILES_FOUND=1
        set "HASH="
        for /f "skip=1 tokens=* delims=" %%A in ('certutil -hashfile "%%F" SHA256') do (
            if not defined HASH (
                set "HASH=%%A"
            )
        )
        set "HASH=!HASH: =!"
        echo SHA256 ^(%%F^) = !HASH!>>"%CHECKSUMS_FILE%"
    )
)

if "%FILES_FOUND%"=="0" (
    echo Error: No release artifacts found.
    exit /b 1
)

echo Checksums generated successfully in %CHECKSUMS_FILE%.
exit /b 0
