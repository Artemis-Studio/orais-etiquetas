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


