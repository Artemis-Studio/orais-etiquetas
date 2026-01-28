@echo off
echo ============================================================
echo VERIFICANDO SERVICO DE IMPRESSAO DO WINDOWS
echo ============================================================
echo.

echo [1] Status do servico Spooler de Impressao:
sc query spooler
echo.

echo [2] Tentando iniciar servico (se estiver parado)...
net start spooler 2>nul
if errorlevel 1 (
    echo Servico ja esta rodando ou nao foi possivel iniciar.
) else (
    echo Servico iniciado com sucesso!
)
echo.

echo ============================================================
echo Verificacao concluida!
echo ============================================================
pause
