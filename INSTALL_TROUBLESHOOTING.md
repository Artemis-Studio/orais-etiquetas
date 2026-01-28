# Guia de Solução de Problemas de Instalação

## Problema: Python 3.14.2 e Compatibilidade

Python 3.14.2 é muito recente e algumas bibliotecas ainda não têm suporte completo ou wheels pré-compilados.

### Solução 1: Usar Python 3.12 ou 3.11 (Recomendado)

Para melhor compatibilidade, use Python 3.12 ou 3.11:

1. Baixe Python 3.12 do site oficial: https://www.python.org/downloads/
2. Instale Python 3.12
3. Use Python 3.12 para o projeto:

```bash
# Verificar versão
py -3.12 --version

# Instalar dependências com Python 3.12
py -3.12 -m pip install -r requirements.txt
```

### Solução 2: Instalar sem dependências opcionais

Se precisar usar Python 3.14, tente instalar sem as dependências que precisam compilar:

```bash
python -m pip install --no-build-isolation -r requirements.txt
```

Ou use a versão mínima:

```bash
python -m pip install -r requirements-minimal.txt
```

### Solução 3: Instalar pacotes individualmente

Instale os pacotes um por um para identificar qual está causando problema:

```bash
python -m pip install fastapi
python -m pip install uvicorn
python -m pip install pywin32
python -m pip install pyyaml
python -m pip install pydantic
python -m pip install python-multipart
python -m pip install requests
python -m pip install click
```

### Solução 4: Usar ambiente virtual

Crie um ambiente virtual isolado:

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### Solução 5: Instalar pywin32 do GitHub (se necessário)

Se o pywin32 não instalar, tente a versão de desenvolvimento:

```bash
python -m pip install git+https://github.com/mhammond/pywin32.git
```

## Erros Comuns

### Erro: "Acesso negado. (5)" ao instalar o serviço Windows

**Causa**: A instalação do serviço exige **Executar como Administrador**. O pywin32 precisa copiar DLLs e registrar o serviço.

**Solução**:
1. Feche outros terminais que usem Python (evita bloquear DLLs).
2. Clique com o botão direito em **install_with_embedded_python.bat** (ou **install_service.bat**) e escolha **"Executar como administrador"**.
3. Ou abra CMD/PowerShell **como Administrador** (botão direito no menu Iniciar), vá até a pasta do projeto e execute o script.

Se usar **install_with_embedded_python.bat**, ele pode perguntar se deseja abrir como Administrador; aceite para subir com permissões elevadas.

### Erro: "Python não encontrado" / "pip não é reconhecido" (com Python embeddable)

**Causa**: O Python embeddable (`python312\`) não está no PATH. Os comandos `python` e `pip` só funcionam se o Python global estiver no PATH.

**Solução**:
- Use os scripts `.bat` do projeto, que detectam o Python embeddable:
  - **run_api.bat** – roda a API (sem serviço): dê dois cliques ou execute no terminal.
  - **install_service.bat** – instala dependências e serviço; usa `python312\` se existir. Execute **como Administrador**.
- Para instalar o serviço com embeddable: use **install_with_embedded_python.bat** **como Administrador** (ele usa o Python em `python312\`).
- Para comandos manuais, use o caminho completo, por exemplo:
  ```bat
  "C:\Users\remoto\Desktop\orais-etiquetas\python312\python.exe" run_api.py
  "C:\Users\remoto\Desktop\orais-etiquetas\python312\python.exe" -m pip install -r requirements.txt
  ```

### Erro: "subprocess-exited-with-error"

**Causa**: Algum pacote precisa compilar e não tem wheel pré-compilado para Python 3.14.

**Solução**: Use Python 3.12 ou 3.11.

### Erro: "No matching distribution found for pywin32==306"

**Causa**: Versão específica não disponível para sua versão do Python.

**Solução**: Use `pywin32>=311` ou instale a versão mais recente disponível.

### Erro: "pip não é reconhecido"

**Causa**: pip não está no PATH.

**Solução**: Use `python -m pip` ao invés de `pip`.

## Verificação

Após instalar, verifique se tudo está funcionando:

```bash
python cli.py validate-setup
```

Se funcionar, você verá:
```
✅ Sistema configurado corretamente!
```

## Recomendação Final

**Para produção, use Python 3.12 ou 3.11** - essas versões têm melhor suporte de bibliotecas e são mais estáveis.


