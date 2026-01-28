# Guia: Instalar Impressora para Usuário Remoto

## 🔍 Situação Atual

O diagnóstico confirmou que o usuário `remoto` não tem nenhuma impressora instalada:
- ✗ Nenhuma impressora local
- ✗ Nenhuma impressora conectada
- ✗ Nenhuma impressora compartilhada
- ✗ Nenhuma impressora padrão

## ✅ Soluções (Escolha uma)

### Solução 1: Instalar Impressora Localmente (Recomendado)

**Passo a passo:**

1. **Faça login como usuário `remoto`**

2. **Abra Configurações do Windows:**
   - Pressione `Win + I`
   - Ou clique no menu Iniciar > Configurações

3. **Navegue até Impressoras:**
   - Clique em **"Dispositivos"**
   - Clique em **"Impressoras e scanners"**

4. **Adicione a impressora:**
   - Clique no botão **"Adicionar impressora ou scanner"**
   - Aguarde o Windows buscar impressoras disponíveis
   - Se sua impressora aparecer, clique nela e siga o assistente
   - Se não aparecer, clique em **"A impressora que eu quero não está listada"**

5. **Opções de instalação:**
   - **Por nome:** `\\NOME_DO_COMPUTADOR\NOME_DA_IMPRESSORA`
   - **Por endereço IP:** `http://192.168.1.XXX` (se for impressora de rede)
   - **Por porta:** Selecione uma porta existente ou crie nova

6. **Instale os drivers:**
   - O Windows tentará instalar automaticamente
   - Se não encontrar, você precisará dos drivers da impressora

7. **Defina como padrão (opcional):**
   - Após instalar, clique com botão direito na impressora
   - Selecione **"Definir como impressora padrão"**

8. **Teste a instalação:**
   ```bash
   listar_impressoras.bat
   ```

---

### Solução 2: Conectar a Impressora Compartilhada

**Se outro usuário/computador já tem a impressora:**

1. **No computador com a impressora instalada:**
   - Abra **Painel de Controle** > **Dispositivos e Impressoras**
   - Clique com botão direito na impressora
   - Selecione **"Propriedades da impressora"**
   - Vá na aba **"Compartilhamento"**
   - Marque **"Compartilhar esta impressora"**
   - Dê um nome (ex: `Zebra_ZT230`)
   - Clique em **OK**

2. **No usuário `remoto`:**
   - Abra **Configurações** > **Impressoras e scanners**
   - Clique em **"Adicionar impressora ou scanner"**
   - Clique em **"A impressora que eu quero não está listada"**
   - Selecione **"Selecionar uma impressora compartilhada por nome"**
   - Digite: `\\NOME_DO_COMPUTADOR\NOME_DA_IMPRESSORA`
   - Exemplo: `\\ESCRITORIO2\Zebra_ZT230`
   - Clique em **Avançar** e siga o assistente

---

### Solução 3: Usar Impressora de Rede (IP)

**Se a impressora tem endereço IP na rede:**

1. **Descubra o IP da impressora:**
   - Na própria impressora, imprima a página de configuração
   - Ou verifique no roteador/switch

2. **Adicione a impressora:**
   - Abra **Configurações** > **Impressoras e scanners**
   - Clique em **"Adicionar impressora ou scanner"**
   - Clique em **"A impressora que eu quero não está listada"**
   - Selecione **"Adicionar uma impressora usando um endereço TCP/IP ou nome de host"**
   - Digite o IP (ex: `192.168.1.100`)
   - Clique em **Avançar** e siga o assistente

---

### Solução 4: Executar API como Administrador

**Pode dar acesso a mais impressoras:**

1. **Pare a API atual** (se estiver rodando)

2. **Execute como Administrador:**
   - Clique com botão direito em `run_api.bat`
   - Selecione **"Executar como administrador"**

3. **Ou configure o serviço para rodar como Administrador:**
   - Abra **Serviços** (`services.msc`)
   - Encontre **"LabelPrintingAPI"**
   - Clique com botão direito > **Propriedades**
   - Vá na aba **"Fazer logon como"**
   - Selecione **"Conta do sistema local"** ou configure uma conta com permissões

---

## 🔧 Verificação Após Instalação

Após instalar a impressora, execute:

```bash
# 1. Listar impressoras
listar_impressoras.bat

# 2. Diagnóstico completo
diagnostico.bat

# 3. Verificar via API (se estiver rodando)
curl http://localhost:8000/printers
```

## ⚙️ Configurar no config.yaml

Depois que a impressora aparecer, configure em `config/config.yaml`:

```yaml
printer:
  default_printer: "Nome_Exato_da_Impressora"
```

**Importante:** Use o nome **exato** que aparece na listagem!

## 🚨 Problemas Comuns

### "Não consigo encontrar a impressora"

- Verifique se a impressora está ligada
- Verifique se está na mesma rede
- Tente pelo IP diretamente
- Verifique firewall/antivírus

### "Erro ao instalar drivers"

- Baixe os drivers do site do fabricante
- Execute a instalação manualmente
- Use drivers genéricos se disponível

### "Acesso negado"

- Execute como Administrador
- Verifique permissões de compartilhamento
- Verifique se o serviço de impressão está rodando

## 📞 Verificar Serviço de Impressão

```bash
# Verificar status
sc query spooler

# Iniciar se estiver parado
net start spooler
```

## ✅ Próximos Passos

1. **Instale a impressora** usando uma das soluções acima
2. **Execute `listar_impressoras.bat`** para confirmar
3. **Configure em `config.yaml`** (opcional, mas recomendado)
4. **Reinicie a API** para aplicar as mudanças
5. **Teste uma impressão** via API

---

**Dica:** A forma mais rápida geralmente é instalar a impressora diretamente pelo Windows usando Configurações > Impressoras e scanners.
