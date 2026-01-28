@echo off
echo ============================================================
echo GUIA RAPIDO: INSTALAR DRIVER ZEBRA
echo ============================================================
echo.

echo Este script ajuda a instalar drivers Zebra.
echo.
echo OPCOES:
echo   1. Abrir site da Zebra para download
echo   2. Verificar se ja existe driver instalado
echo   3. Instrucoes de instalacao manual
echo.
echo Escolha uma opcao (1-3) ou pressione qualquer tecla para sair:
set /p opcao=

if "%opcao%"=="1" (
    echo.
    echo Abrindo site da Zebra...
    start https://www.zebra.com/us/en/support-downloads/printers.html
    echo.
    echo Site aberto! Baixe o driver para seu modelo.
    echo.
    echo Modelos comuns:
    echo   - ZT230: ZDesigner Driver
    echo   - ZD420: ZDesigner Driver
    echo   - ZD620: ZDesigner Driver
    echo.
    pause
    exit /b
)

if "%opcao%"=="2" (
    echo.
    echo Verificando drivers Zebra instalados...
    echo.
    wmic printer get Name,DriverName | findstr /i "zebra zdesigner"
    if errorlevel 1 (
        echo Nenhum driver Zebra encontrado.
    )
    echo.
    pause
    exit /b
)

if "%opcao%"=="3" (
    echo.
    echo ============================================================
    echo INSTRUCOES DE INSTALACAO MANUAL
    echo ============================================================
    echo.
    echo 1. Baixe o driver do site da Zebra
    echo 2. Execute o instalador como Administrador
    echo 3. Siga o assistente de instalacao
    echo 4. Conecte a impressora quando solicitado
    echo 5. Execute listar_impressoras.bat para verificar
    echo.
    echo Para abrir o site, escolha opcao 1.
    echo.
    pause
    exit /b
)

echo.
echo Saindo...
timeout /t 2 >nul
