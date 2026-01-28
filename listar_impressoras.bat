@echo off
REM Script para listar impressoras usando Python embeddable ou PATH
cd /d "%~dp0"
set "PYTHONPATH=%~dp0"

echo ============================================================
echo LISTANDO IMPRESSORAS DISPONIVEIS
echo ============================================================
echo.

REM Usar Python embeddable se existir; senao usar python do PATH
if exist "%~dp0python312\python.exe" (
    "%~dp0python312\python.exe" "%~dp0cli.py" list-printers
) else (
    python "%~dp0cli.py" list-printers
)

if errorlevel 1 (
    echo.
    echo ERRO ao listar impressoras!
    pause
)
