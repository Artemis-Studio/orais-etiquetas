@echo off
cd /d "%~dp0"
if not exist "%~dp0logs" mkdir "%~dp0logs"

set "PYEXE="
if exist "%~dp0python312\python.exe" (
    set "PYEXE=%~dp0python312\python.exe"
) else (
    set "PYEXE=python"
)

set "WRK=%~dp0"
if "%WRK:~-1%"=="\" set "WRK=%WRK:~0,-1%"

powershell -NoProfile -Command "Start-Process -FilePath \"%PYEXE%\" -ArgumentList 'run_api.py' -WorkingDirectory \"%WRK%\" -WindowStyle Hidden"

echo API iniciada em background.
echo Logs: logs\api.log
echo Para parar: Get-Process -Name python ^| Stop-Process -Force
echo.
