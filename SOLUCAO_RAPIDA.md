# Solução Rápida: Instalar Impressora para Usuário Remoto

## ✅ Status Atual

- ✅ Serviço de impressão está rodando
- ❌ Nenhuma impressora instalada para usuário `remoto`

## 🎯 Solução: Instalar Impressora

### Método 1: Via Interface do Windows (Mais Fácil)

1. **Pressione `Win + I`** (abre Configurações)

2. **Vá em:** Dispositivos > Impressoras e scanners

3. **Clique em:** "Adicionar impressora ou scanner"

4. **Aguarde** o Windows buscar impressoras automaticamente

5. **Se aparecer sua impressora:**
   - Clique nela
   - Siga o assistente de instalação
   - Pronto!

6. **Se NÃO aparecer:**
   - Clique em **"A impressora que eu quero não está listada"**
   - Escolha uma opção:
     - **Por nome:** `\\COMPUTADOR\IMPRESSORA` (se compartilhada)
     - **Por IP:** `http://192.168.1.XXX` (se for de rede)
     - **Por porta:** Selecione uma porta existente

### Método 2: Descobrir Impressoras na Rede

Execute:
```bash
descobrir_impressoras_rede.bat
```

Isso mostra impressoras compartilhadas e disponíveis na rede.

### Método 3: Adicionar por IP Direto

Se você sabe o IP da impressora:

1. **Configurações** > **Impressoras e scanners**
2. **"Adicionar impressora ou scanner"**
3. **"A impressora que eu quero não está listada"**
4. **"Adicionar uma impressora usando um endereço TCP/IP ou nome de host"**
5. **Digite o IP** (ex: `192.168.1.100`)
6. **Avançar** e siga o assistente

## 🔍 Verificar Após Instalar

```bash
listar_impressoras.bat
```

Deve mostrar a impressora instalada!

## ⚙️ Configurar na API

Depois que aparecer na listagem, edite `config/config.yaml`:

```yaml
printer:
  default_printer: "Nome_Exato_da_Impressora"
```

**Use o nome EXATO que aparece em `listar_impressoras.bat`!**

## 🚨 Se Não Conseguiu Instalar

### Verificar se há outra impressora instalada em outro usuário:

1. **Faça login com outro usuário** que tenha a impressora
2. **Compartilhe a impressora:**
   - Painel de Controle > Dispositivos e Impressoras
   - Botão direito na impressora > Propriedades
   - Aba "Compartilhamento" > Marcar "Compartilhar esta impressora"
3. **Volte para usuário `remoto`** e conecte via `\\COMPUTADOR\IMPRESSORA`

### Ou instale drivers manualmente:

1. **Baixe os drivers** da impressora do site do fabricante
2. **Execute a instalação** como Administrador
3. **Depois adicione a impressora** nas Configurações

## 📝 Resumo

1. ✅ Serviço de impressão OK
2. ⚠️ Precisa instalar impressora para usuário `remoto`
3. 📋 Use Configurações > Impressoras e scanners
4. ✅ Execute `listar_impressoras.bat` após instalar
5. ⚙️ Configure em `config.yaml` (opcional)

---

**Dica:** A forma mais rápida é abrir Configurações do Windows e adicionar a impressora diretamente pela interface gráfica!
