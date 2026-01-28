# Como Selecionar a Impressora nas Requisições

A impressora é selecionada através do campo `printer_name` no JSON da requisição.

## 📋 Formas de Selecionar a Impressora

### 1. **Impressora Padrão** (campo vazio ou omitido)
```json
{
  "label_type": "produto",
  "data": { ... },
  "printer_name": ""  // ou omitir este campo
}
```
Usa a impressora padrão do sistema Windows.

### 2. **Impressora Específica** (nome exato)
```json
{
  "label_type": "produto",
  "data": { ... },
  "printer_name": "Zebra_ZT230"
}
```
Usa a impressora com o nome exato especificado.

---

## 🔍 Como Descobrir o Nome da Impressora

### Via CLI
```bash
python cli.py list-printers
```

### Via API
```bash
curl http://100.80.127.36:8000/printers
```

### Via Python
```python
import requests
response = requests.get("http://100.80.127.36:8000/printers")
print(response.json())
```

**Exemplo de resposta:**
```json
{
  "printers": ["Zebra_ZT230", "HP_LaserJet"],
  "default": "Zebra_ZT230",
  "count": 2
}
```

---

## 📝 Exemplos Práticos

### Via cURL com Arquivo JSON

**Opção 1: Editar o arquivo JSON diretamente**
Edite `requisicao_completa.json` e altere:
```json
"printer_name": "Zebra_ZT230"
```

Depois execute:
```bash
curl_completo.bat
```

**Opção 2: Usar script com parâmetro**
```bash
curl_completo.bat "Zebra_ZT230"
```

**Opção 3: Usar arquivo JSON específico**
```bash
# Use o arquivo requisicao_com_impressora.json
type requisicao_com_impressora.json | curl.exe -X POST http://100.80.127.36:8000/print -H "Content-Type: application/json" -d "@-"
```

### Via CLI
```bash
python cli.py print-via-api \
  --codigo "1420" \
  --descricao "JG DENTE ENDO 21 AO 27 RADIO" \
  --printer "Zebra_ZT230"
```

### Via Python
```python
import requests

data = {
    "label_type": "produto",
    "data": {
        "codigo": "1420",
        "descricao": "JG DENTE ENDO 21 AO 27 RADIO"
    },
    "printer_name": "Zebra_ZT230"  # Especifica a impressora
}

response = requests.post(
    "http://100.80.127.36:8000/print",
    json=data,
    headers={"Content-Type": "application/json"}
)
print(response.json())
```

### Via PowerShell
```powershell
$json = @{
    label_type = "produto"
    data = @{
        codigo = "1420"
        descricao = "JG DENTE ENDO 21 AO 27 RADIO"
    }
    printer_name = "Zebra_ZT230"
} | ConvertTo-Json -Depth 10

Invoke-WebRequest -Uri "http://100.80.127.36:8000/print" `
    -Method POST `
    -ContentType "application/json" `
    -Body $json
```

---

## 🎯 Resumo

| Método | Campo | Valor |
|--------|-------|-------|
| Impressora Padrão | `printer_name` | `""` ou omitir |
| Impressora Específica | `printer_name` | `"Nome_Exato_da_Impressora"` |

**Importante:**
- O nome da impressora deve ser **exatamente** como aparece no Windows
- Use `python cli.py list-printers` para ver os nomes disponíveis
- Se o nome estiver errado, a API usará a impressora padrão

---

## 📚 Arquivos Disponíveis

1. **`requisicao_completa.json`** - Com `printer_name: ""` (padrão)
2. **`requisicao_com_impressora.json`** - Com `printer_name: "Zebra_ZT230"` (exemplo)
3. **`curl_completo.bat`** - Aceita nome da impressora como parâmetro
4. **`curl_com_impressora.bat`** - Script específico para impressora
