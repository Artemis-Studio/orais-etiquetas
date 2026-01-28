@echo off
echo ============================================================
echo DESCOBRINDO USUARIOS DO SISTEMA
echo ============================================================
echo.

echo [1] Usuario atual (remoto):
whoami
echo.

echo [2] Todos os usuarios do sistema:
echo.
for /f "tokens=1" %%u in ('wmic useraccount get name ^| findstr /v "Name" ^| findstr /v "^$"') do (
    echo   - %%u
)
echo.

echo [3] Usuarios locais (nao do dominio):
echo.
for /f "tokens=1" %%u in ('wmic useraccount where "LocalAccount=True" get name ^| findstr /v "Name" ^| findstr /v "^$"') do (
    echo   - %%u
)
echo.

echo ============================================================
echo INSTRUCOES:
echo ============================================================
echo.
echo O usuario padrao (sem senha) geralmente e um dos usuarios
echo locais listados acima. Geralmente e o primeiro usuario criado
echo no sistema ou o usuario "Administrador".
echo.
echo Para configurar o servico para usar esse usuario:
echo   1. Execute: configurar_servico_usuario_padrao.bat
echo   2. Digite o nome do usuario padrao quando solicitado
echo.
echo ============================================================
pause
