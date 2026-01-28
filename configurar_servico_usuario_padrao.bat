@echo off
REM Script para configurar o servico para rodar como usuario padrao
REM Requer execucao como Administrador

echo ============================================================
echo CONFIGURAR SERVICO PARA USUARIO PADRAO
echo ============================================================
echo.

REM Verifica se esta como Administrador
net session >nul 2>&1
if errorlevel 1 (
    echo ERRO: Este script precisa ser executado como Administrador!
    echo.
    echo Clique com botao direito e escolha "Executar como administrador"
    pause
    exit /b 1
)

echo [1] Descobrindo usuarios do sistema...
echo.
for /f "tokens=1" %%u in ('wmic useraccount get name ^| findstr /v "Name" ^| findstr /v "^$"') do (
    echo   - %%u
)
echo.

echo [2] Digite o nome do usuario padrao (sem senha):
set /p USUARIO_PADRAO=

if "%USUARIO_PADRAO%"=="" (
    echo ERRO: Nome do usuario nao pode ser vazio!
    pause
    exit /b 1
)

echo.
echo [3] Parando servico atual (se estiver rodando)...
net stop LabelPrintingAPI 2>nul
timeout /t 2 >nul

echo.
echo [4] Configurando servico para rodar como: %USUARIO_PADRAO%
echo.
sc config LabelPrintingAPI obj= ".\%USUARIO_PADRAO%" password= ""

if errorlevel 1 (
    echo ERRO: Falha ao configurar servico!
    echo.
    echo Verifique se o nome do usuario esta correto.
    pause
    exit /b 1
)

echo.
echo [5] Configuracao concluida!
echo.
echo [6] Iniciando servico...
net start LabelPrintingAPI

if errorlevel 1 (
    echo.
    echo AVISO: Nao foi possivel iniciar o servico automaticamente.
    echo Tente iniciar manualmente: net start LabelPrintingAPI
) else (
    echo.
    echo Servico iniciado com sucesso!
)

echo.
echo ============================================================
echo VERIFICACAO:
echo ============================================================
echo.
echo Aguarde alguns segundos e verifique:
echo   curl http://localhost:8000/printers
echo.
echo Ou execute: listar_impressoras.bat
echo.
pause
