@echo off
echo ============================================================
echo Teste de Requisicao Completa (sem API key)
echo ============================================================
echo.

echo [1] Verificando status da API...
python cli.py status
echo.

echo [2] Enviando requisicao completa via CLI...
python cli.py print-via-api ^
  --codigo "1420" ^
  --descricao "JG DENTE ENDO 21 AO 27 RADIO" ^
  --descricao2 "PACOS" ^
  --ref "1420" ^
  --pedido "10511" ^
  --codigo-barras "7890000005098" ^
  --lote "10111150126" ^
  --validade "31/12/2025" ^
  --quantidade "10" ^
  --preco "29.90"
echo.

echo [3] Verificando fila...
python cli.py queue --limit 5
echo.

echo ============================================================
echo Teste concluido!
echo ============================================================
pause
