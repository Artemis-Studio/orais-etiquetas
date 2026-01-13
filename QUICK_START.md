# Guia Rápido de Início

## Instalação Rápida

1. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure a API:**
   - Edite `config/config.yaml`
   - Configure a porta e API key (opcional)

3. **Teste a API (modo desenvolvimento):**
   ```bash
   python run_api.py
   ```

4. **Ou instale como serviço Windows:**
   ```bash
   install_service.bat
   ```

## Teste Rápido

1. Inicie a API (se não estiver rodando como serviço):
   ```bash
   python run_api.py
   ```

2. Em outro terminal, teste com o exemplo:
   ```bash
   python example_request.py
   ```

## Integração com n8n

No n8n, use o nó **HTTP Request**:

- **Método:** POST
- **URL:** `http://IP_DO_COMPUTADOR:8000/print`
- **Headers:**
  - `Content-Type: application/json`
  - `X-API-Key: sua-chave` (se configurada)
- **Body (JSON):**
  ```json
  {
    "label_type": "produto",
    "data": {
      "codigo": "12345",
      "descricao": "Produto XYZ",
      "quantidade": 10,
      "preco": "29.90"
    }
  }
  ```

## Comandos Úteis

```bash
# Iniciar serviço
net start LabelPrintingAPI

# Parar serviço
net stop LabelPrintingAPI

# Ver status
sc query LabelPrintingAPI

# Desinstalar serviço
python service/windows_service.py remove
```

## Endpoints Principais

- `POST /print` - Imprimir etiqueta
- `GET /status` - Status do serviço
- `GET /queue` - Ver fila de impressão
- `GET /printers` - Listar impressoras

Veja `README.md` para documentação completa.

