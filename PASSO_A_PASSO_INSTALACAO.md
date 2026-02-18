# Passo a passo – Reinstalação do sistema Orais Etiquetas

Guia para reinstalar a API de impressão de etiquetas após formatação do PC ou mudança de máquina.

---

## 1. Requisitos

- **Windows** 10 ou 11  
- **Python 3.10+**  
- **Impressora Zebra** (ex.: ZDesigner / GC420t) com driver instalado  
- Acesso ao CMD ou PowerShell (SSH ou local)

---

## 2. Instalar Python

1. Baixe o instalador em: https://www.python.org/downloads/
2. Na instalação, marque **"Add Python to PATH"**
3. Use a opção **"Install for all users"** se for usar tarefa agendada como System
4. Confirme o caminho de instalação (ex.: `C:\Program Files\Python312\`)
5. Para conferir:

   ```cmd
   python --version
   where python
   ```

---

## 3. Configurar o projeto

### 3.1 Colocar os arquivos do projeto

Copie ou clone o projeto para a pasta desejada, por exemplo:

```
C:\Users\Usuário\Desktop\Artemis-code\orais-etiquetas
```

### 3.2 Instalar dependências

```cmd
cd C:\Users\Usuário\Desktop\Artemis-code\orais-etiquetas
pip install -r requirements.txt
pip install Pillow
```

### 3.3 Criar arquivo de configuração

Certifique-se de que o arquivo `config/config.yaml` existe. Se não existir, crie a pasta `config` e o arquivo com este conteúdo (ajuste conforme necessário):

```yaml
api:
  host: "0.0.0.0"
  port: 8000
  api_key: ""

printer:
  default_printer: "ZDesigner_Produto"
  timeout: 30
  retry_attempts: 3
  label_dpi: 203
  label_margin_left: 8
  label_margin_right: 8
  use_symmetric_margins: true
  label_margin_top: 2
  label_width_mm: 50
  label_height_mm: 25
  gap_between_columns_mm: 1
  font_scale: 1.25
  logo_path: "assets/logoOrais.jpg"
  logo_margin_right_mm: 4
  logo_height_mm: 6

queue:
  check_interval: 30
  max_retries: 3

logging:
  level: "INFO"
  file: "logs/api.log"
```

### 3.4 Ajustar a impressora no config

Em `config/config.yaml`, altere `default_printer` para o nome exato da impressora no Windows.

Para listar impressoras:

```cmd
python -m cli list-printers
```

### 3.5 Logo (opcional)

- Coloque o arquivo `logoOrais.jpg` em `assets/`
- Se não quiser usar logo, defina `logo_path: ""` no config

---

## 4. Testar manualmente

```cmd
cd C:\Users\Usuário\Desktop\Artemis-code\orais-etiquetas
python run_api.py
```

A API deve iniciar em `http://0.0.0.0:8000`.

Em outro terminal ou no navegador:

```cmd
curl http://localhost:8000/status
```

Ou acesse: http://localhost:8000/docs

Para testar impressão:

```cmd
python -m cli print-label -c TESTE -d "Teste" --codigo-barras 7890000005098 -p "ZDesigner_Produto"
```

Pare a API com **Ctrl+C**.

---

## 5. Iniciar automaticamente ao ligar o PC

### 5.1 Criar tarefa agendada (via CMD/PowerShell)

**1. Descubra o caminho do Python:**

```cmd
where python
```

Exemplo: `C:\Program Files\Python312\python.exe`

**2. Defina a pasta do projeto** (ajuste se mudar o local):

```
C:\Users\Usuário\Desktop\Artemis-code\orais-etiquetas
```

**3. Crie a tarefa agendada:**

```cmd
schtasks /create /tn "OraisEtiquetasAPI" /tr "\"C:\Program Files\Python312\python.exe\" \"C:\Users\Usuário\Desktop\Artemis-code\orais-etiquetas\run_api.py\"" /sc onstart /ru System /rp "" /f
```

**4. Teste a tarefa:**

```cmd
schtasks /run /tn "OraisEtiquetasAPI"
timeout /t 5
curl http://localhost:8000/status
```

**5. Verifique se a API respondeu** (deve retornar `"status":"online"`).

### 5.2 Opção com arquivo .bat

Crie `iniciar_api.bat` dentro da pasta do projeto com:

```batch
@echo off
cd /d "C:\Users\Usuário\Desktop\Artemis-code\orais-etiquetas"
"C:\Program Files\Python312\python.exe" run_api.py
```

Depois crie a tarefa apontando para o .bat:

```cmd
schtasks /create /tn "OraisEtiquetasAPI" /tr "C:\Users\Usuário\Desktop\Artemis-code\orais-etiquetas\iniciar_api.bat" /sc onstart /ru System /rp "" /f
```

---

## 6. Comandos úteis

| Ação | Comando |
|------|---------|
| Iniciar API manualmente | `python run_api.py` |
| Listar impressoras | `python -m cli list-printers` |
| Imprimir 1 etiqueta | `python -m cli print-label -c 1420 -d "Produto" --codigo-barras 7890000005098` |
| Imprimir 2 etiquetas (mesmo conteúdo) | Adicione `--duas-colunas` ao comando acima |
| Calibrar etiquetas | `python -m cli calibrar -p "ZDesigner_Produto"` |
| Rodar tarefa manualmente | `schtasks /run /tn "OraisEtiquetasAPI"` |
| Excluir tarefa | `schtasks /delete /tn "OraisEtiquetasAPI" /f` |
| Ver status da API | `curl http://localhost:8000/status` |

---

## 7. Testar a API (impressão)

**PowerShell:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/print" -Method POST -ContentType "application/json" -Body '{"label_type":"produto","duas_colunas":true,"data":{"codigo":"1420","descricao":"JG DENTE ENDO 21 AO 27 RADIO","descricao2":"PACOS","ref":"1420","pedido":"10511","codigo_barras":"7890000005098","lote":"10111150126","validade":"31/12/2025"}}'
```

**CMD (curl):**

```cmd
curl -X POST http://localhost:8000/print -H "Content-Type: application/json" -d "{\"label_type\":\"produto\",\"duas_colunas\":true,\"data\":{\"codigo\":\"1420\",\"descricao\":\"JG DENTE ENDO 21 AO 27 RADIO\",\"codigo_barras\":\"7890000005098\"}}"
```

---

## 8. Checklist após reinstalação

- [ ] Python instalado e no PATH
- [ ] Projeto copiado para a pasta correta
- [ ] `pip install -r requirements.txt` e `pip install Pillow` executados
- [ ] `config/config.yaml` configurado (impressora, etc.)
- [ ] Impressora instalada e com driver
- [ ] `python run_api.py` funciona
- [ ] `curl http://localhost:8000/status` retorna `"status":"online"`
- [ ] Tarefa agendada criada com `schtasks`
- [ ] Reinício do PC testado (API inicia sozinha)

---

## 9. Solução de problemas

**API não inicia:**
- Conferir caminho do Python e do projeto no comando da tarefa
- Verificar se a porta 8000 está livre
- Checar `logs/api.log`

**Impressora não encontrada:**
- `python -m cli list-printers` para ver o nome exato
- Atualizar `default_printer` em `config/config.yaml`

**Tarefa não roda ao reiniciar:**
- Usar caminho completo do Python no `schtasks`
- Conferir se a tarefa existe: `schtasks /query /tn "OraisEtiquetasAPI"`
- Ver histórico: Agendador de Tarefas → OraisEtiquetasAPI → Histórico
