@echo off
REM Script para executar a API com credenciais do usuario padrao
REM Alternativa ao servico Windows

echo ============================================================
echo EXECUTAR API COM USUARIO PADRAO
echo ============================================================
echo.

echo [1] Descobrindo usuarios disponiveis...
echo.
for /f "tokens=1" %%u in ('wmic useraccount where "LocalAccount=True" get name ^| findstr /v "Name" ^| findstr /v "^$"') do (
    echo   - %%u
)
echo.

echo [2] Digite o nome do usuario padrao:
set /p USUARIO_PADRAO=

if "%USUARIO_PADRAO%"=="" (
    echo ERRO: Nome do usuario nao pode ser vazio!
    pause
    exit /b 1
)

echo.
echo [3] Parando processos Python existentes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul

echo.
echo [4] Executando API como usuario: %USUARIO_PADRAO%
echo.
echo NOTA: Como o usuario padrao nao tem senha, pressione ENTER
echo       quando solicitado a senha.
echo.

cd /d "%~dp0"

REM Usa Python embeddable se existir
if exist "%~dp0python312\python.exe" (
    runas /user:%USUARIO_PADRAO "%~dp0python312\python.exe run_api.py"
) else (
    runas /user:%USUARIO_PADRAO "python run_api.py"
)

echo.
echo ============================================================
echo API executada!
echo ============================================================
echo.
echo Para verificar se esta rodando:
echo   curl http://localhost:8000/status
echo.
echo Para parar:
echo   taskkill /F /IM python.exe
echo.
pause
