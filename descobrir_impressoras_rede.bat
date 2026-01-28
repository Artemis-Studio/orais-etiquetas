@echo off
echo ============================================================
echo DESCOBRINDO IMPRESSORAS NA REDE
echo ============================================================
echo.

echo [1] Listando impressoras compartilhadas na rede local...
echo.
net view | findstr /C:"\\"
echo.

echo [2] Tentando descobrir impressoras via WSD (Web Services for Devices)...
echo     (Isso pode levar alguns segundos...)
echo.
powershell -Command "Get-Printer | Format-Table Name, DriverName, PortName -AutoSize" 2>nul
echo.

echo [3] Verificando impressoras instaladas via PowerShell...
echo.
powershell -Command "Get-Printer | Select-Object Name, PrinterStatus, DriverName | Format-List" 2>nul
if errorlevel 1 (
    echo Nenhuma impressora encontrada via PowerShell.
)
echo.

echo ============================================================
echo INSTRUCOES:
echo ============================================================
echo.
echo Se apareceram impressoras acima, voce pode conecta-las:
echo   1. Abra Configuracoes do Windows (Win+I)
echo   2. Va em Dispositivos ^> Impressoras e scanners
echo   3. Clique em "Adicionar impressora ou scanner"
echo   4. Se a impressora aparecer, selecione e instale
echo.
echo Se nao apareceu nenhuma impressora:
echo   - A impressora precisa ser instalada manualmente
echo   - Ou compartilhada por outro usuario/computador
echo   - Ou adicionada pelo IP se for impressora de rede
echo.
echo ============================================================
pause
