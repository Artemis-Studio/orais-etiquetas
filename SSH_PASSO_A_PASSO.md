# Passo a passo – Uso via SSH no Windows

Guia para instalar, iniciar e manter a API de etiquetas rodando quando você está conectado por **SSH** no Windows.

---

## 1. Conectar via SSH

No seu computador local:

```bash
ssh usuario@IP_DO_WINDOWS
```

Exemplo: `ssh remoto@192.168.1.100`

---

## 2. Ir para a pasta do projeto

```powershell
cd C:\Users\remoto\Desktop\orais-etiquetas
```

*(Ajuste o caminho se o projeto estiver em outro lugar.)*

---

## 3. Escolher: com serviço Windows ou só API em background

| Opção | Precisa admin? | Mantém rodando após desconectar SSH? |
|-------|----------------|--------------------------------------|
| **Serviço Windows** | Sim | Sim |
| **API em background** | Não | Sim |

---

## Opção A – Com serviço Windows (recomendado em produção)

Requer **PowerShell ou CMD como Administrador**. Em SSH, a sessão costuma **não** ser admin. Você precisa de uma sessão elevada.

### 3A.1. Abrir PowerShell como Administrador (na máquina Windows)

Se você tem acesso físico ou RDP:

1. Menu Iniciar → digite **PowerShell**
2. Botão direito em **Windows PowerShell** → **Executar como administrador**
3. Na janela que abrir:
   ```powershell
   cd C:\Users\remoto\Desktop\orais-etiquetas
   ```

Se você **só** usa SSH e consegue rodar comandos elevados (ex.: via PsExec, Task Scheduler ou SSH configurado como admin), use essa mesma pasta nos comandos abaixo.

### 3A.2. Instalar Python embeddable + dependências + serviço

**Primeira vez** (ou se ainda não tiver a pasta `python312`):

```powershell
.\install_with_embedded_python.bat
```

- O script verifica se está como admin e pode pedir para abrir elevado; aceite.
- Ele baixa o Python embeddable, instala dependências e instala o serviço **LabelPrintingAPI**.

Se já tiver `python312` e só quiser **reinstalar o serviço** (com admin):

```powershell
.\python312\python.exe -m pip install -r requirements.txt
.\python312\python.exe .\service\windows_service.py install
```

### 3A.3. Iniciar o serviço

Ainda **como Administrador**:

```powershell
net start LabelPrintingAPI
```

O serviço fica rodando em segundo plano, mesmo depois de fechar o SSH.

### 3A.4. Comandos úteis (sempre como admin)

```powershell
net start LabelPrintingAPI    # Iniciar
net stop LabelPrintingAPI     # Parar
sc query LabelPrintingAPI     # Ver status
```

### 3A.5. Desinstalar o serviço (se precisar)

```powershell
.\python312\python.exe .\service\windows_service.py remove
```

---

## Opção B – API em background (sem serviço, sem admin)

Não precisa de Administrador. A API roda em processo separado e continua ativa após desconectar o SSH.

### 3B.1. Garantir que há Python e dependências

Se já rodou `install_with_embedded_python.bat` antes, deve existir `python312\`. Caso contrário, execute **como Administrador** (uma vez) na máquina Windows:

```powershell
.\install_with_embedded_python.bat
```

Depois disso, você pode usar a Opção B **sem** admin.

### 3B.2. Iniciar a API em background via SSH

Na sua sessão SSH (normal, sem admin):

```powershell
cd C:\Users\remoto\Desktop\orais-etiquetas
.\run_api_background.bat
```

Ou manualmente:

```powershell
cd C:\Users\remoto\Desktop\orais-etiquetas
Start-Process -FilePath ".\python312\python.exe" -ArgumentList "run_api.py" -WindowStyle Hidden -WorkingDirectory "C:\Users\remoto\Desktop\orais-etiquetas"
```
*(Ajuste o caminho para a pasta do seu projeto.)*

A API sobe em background e segue rodando depois de você sair do SSH.

### 3B.3. Ver se a API está rodando

**No CMD:**
```cmd
tasklist | findstr python
curl http://localhost:8000/status
```

**No PowerShell:**
```powershell
Get-Process -Name python -ErrorAction SilentlyContinue
curl http://localhost:8000/status
```

### 3B.4. Parar a API (quando estiver em background)

**No CMD:**
```cmd
taskkill /F /IM python.exe
```

**No PowerShell:**
```powershell
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force
```

*(Isso encerra todos os processos Python. Se houver outros, use o PID específico.)*

### 3B.5. API não sobe / `curl` falha ("Could not connect")

1. **Rodar em primeiro plano** para ver o erro na tela:
   ```cmd
   cd C:\Users\remoto\Desktop\orais-etiquetas
   .\run_api.bat
   ```
   Deixe rodar; o que aparecer no terminal é o erro (import, porta, etc.).

2. **Ver logs de erro do background:**
   ```cmd
   type logs\api_background_err.txt
   type logs\api.log
   ```
   O `run_api_background.bat` grava erros de arranque em `logs\api_background_err.txt`.

---

## 4. Testar a API

Com a API rodando (serviço ou background):

```powershell
.\python312\python.exe example_request.py
```

Ou, se `python` estiver no PATH:

```powershell
python example_request.py
```

Ou via HTTP:

```powershell
curl http://localhost:8000/status
```

---

## 5. Logs

- Serviço ou API: logs em `config\config.yaml` → `logging.file` (ex.: `logs/api.log`).
- Ver últimas linhas:

**No CMD:**
```cmd
type logs\api.log
```

**No PowerShell:**
```powershell
Get-Content .\logs\api.log -Tail 50
```

---

## 6. Resumo rápido (SSH)

**Com serviço (precisa admin uma vez para instalar e para start/stop):**

```powershell
cd C:\Users\remoto\Desktop\orais-etiquetas
.\install_with_embedded_python.bat    # 1x, como Admin
net start LabelPrintingAPI            # como Admin, sempre que reiniciar o PC
```

**Sem serviço (não precisa admin):**

```powershell
cd C:\Users\remoto\Desktop\orais-etiquetas
.\run_api_background.bat
```

Depois pode desconectar o SSH; a API continua rodando.
