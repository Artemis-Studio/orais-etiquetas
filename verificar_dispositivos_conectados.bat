@echo off
echo ============================================================
echo VERIFICANDO DISPOSITIVOS DE IMPRESSAO CONECTADOS
echo ============================================================
echo.

echo [1] Listando dispositivos USB conectados (pode incluir impressoras)...
echo.
wmic path Win32_USBControllerDevice get Dependent 2>nul | findstr /C:"USB"
echo.

echo [2] Verificando portas de impressao disponiveis...
echo.
wmic printerport get Name,Description 2>nul
echo.

echo [3] Verificando impressoras via WMI (inclui sem drivers)...
echo.
wmic printer get Name,Status,Default,PortName 2>nul
echo.

echo [4] Verificando dispositivos de impressao via PowerShell...
echo.
powershell -Command "Get-PnpDevice -Class Printer | Format-Table FriendlyName, Status, InstanceId -AutoSize" 2>nul
echo.

echo ============================================================
echo INTERPRETACAO:
echo ============================================================
echo.
echo Se apareceram dispositivos acima mas nao aparecem em
echo "listar_impressoras.bat", significa que faltam drivers!
echo.
echo PROXIMOS PASSOS:
echo   1. Identifique o modelo da impressora
echo   2. Baixe os drivers do site do fabricante
echo   3. Instale os drivers
echo   4. Depois adicione a impressora nas Configuracoes
echo.
echo ============================================================
pause
