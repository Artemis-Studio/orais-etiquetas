"""CLI para gerenciamento e validação da API de Impressão de Etiquetas."""
import click
import requests
import json
import sys
import os
from typing import Optional
from pathlib import Path

# Configura encoding UTF-8 para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from api.printer import PrinterManager
from api.zpl_generator import ZPLGenerator
from config.config_loader import get_config


@click.group()
@click.option('--api-url', default='http://localhost:8000', 
              help='URL da API (padrão: http://localhost:8000)')
@click.option('--api-key', default=None, 
              help='API key para autenticação (opcional)')
@click.pass_context
def cli(ctx, api_url, api_key):
    """CLI para gerenciamento da API de Impressão de Etiquetas."""
    ctx.ensure_object(dict)
    ctx.obj['api_url'] = api_url
    ctx.obj['api_key'] = api_key


def get_headers(ctx):
    """Retorna headers para requisições HTTP."""
    headers = {"Content-Type": "application/json"}
    if ctx.obj.get('api_key'):
        headers["X-API-Key"] = ctx.obj['api_key']
    return headers


@cli.command()
@click.pass_context
def list_printers(ctx):
    """Lista todas as impressoras disponíveis no sistema."""
    click.echo("[BUSCANDO] Buscando impressoras disponiveis...\n")
    
    try:
        # Usa a biblioteca diretamente para listar impressoras locais
        printer_manager = PrinterManager()
        printers = printer_manager.list_printers()
        default = printer_manager.get_default_printer()
        
        if not printers:
            click.echo("[ERRO] Nenhuma impressora encontrada no sistema.")
            return
        
        click.echo(f"[LISTA] Impressoras encontradas ({len(printers)}):\n")
        
        for i, printer in enumerate(printers, 1):
            marker = "[*]" if printer == default else "   "
            click.echo(f"{marker} {i}. {printer}")
            if printer == default:
                click.echo("     (Impressora padrao do sistema)")
        
        click.echo(f"\n[OK] Total: {len(printers)} impressora(s)")
        
    except Exception as e:
        click.echo(f"[ERRO] Erro ao listar impressoras: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--printer', '-p', default=None, 
              help='Nome da impressora (deixe vazio para usar padrão)')
@click.pass_context
def test_both_columns(ctx, printer):
    """Testa as duas colunas - imprime mesma etiqueta em esquerda e direita."""
    click.echo("[TESTE] Testando DUAS COLUNAS (esquerda + direita)...\n")
    try:
        printer_manager = PrinterManager()
        printer_name = printer_manager.get_printer_name(printer)
        if not printer_name:
            click.echo("[ERRO] Nenhuma impressora disponivel.")
            sys.exit(1)
        click.echo(f"[IMPRESSORA] {printer_name}")
        click.echo("[ENVIANDO] Etiqueta de teste nas duas colunas...")
        zpl_generator = ZPLGenerator()
        zpl = zpl_generator.generate_dual_column_test_label()
        success = printer_manager.print_zpl(zpl, printer_name)
        if success:
            click.echo("[OK] Verifique as duas etiquetas (esquerda e direita)")
        else:
            click.echo("[ERRO] Falha ao enviar impressao.")
            sys.exit(1)
    except Exception as e:
        click.echo(f"[ERRO] {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--printer', '-p', default=None, 
              help='Nome da impressora (deixe vazio para usar padrão)')
@click.pass_context
def test_printer(ctx, printer):
    """Testa a impressão em uma impressora."""
    click.echo("[TESTE] Testando impressao...\n")
    
    try:
        printer_manager = PrinterManager()
        printer_name = printer_manager.get_printer_name(printer)
        
        if not printer_name:
            click.echo("[ERRO] Nenhuma impressora disponivel.")
            sys.exit(1)
        
        click.echo(f"[IMPRESSORA] Impressora: {printer_name}")
        click.echo("[ENVIANDO] Enviando etiqueta de teste...")
        
        # Gera ZPL de teste
        zpl_generator = ZPLGenerator()
        test_data = {
            "codigo": "TESTE",
            "descricao": "Etiqueta de Teste",
            "quantidade": "1",
            "codigo_barras": "1234567890123"
        }
        zpl = zpl_generator.generate_product_label(test_data)
        
        # Tenta imprimir
        success = printer_manager.print_zpl(zpl, printer_name)
        
        if success:
            click.echo("[OK] Impressao de teste enviada com sucesso!")
            click.echo(f"   Verifique a impressora: {printer_name}")
        else:
            click.echo("[ERRO] Falha ao enviar impressao.")
            click.echo("   Verifique se a impressora está ligada e conectada.")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"[ERRO] Erro ao testar impressao: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--printer', '-p', default=None,
              help='Nome da impressora')
@click.option('--codigo', '-c', required=True,
              help='Código do produto')
@click.option('--descricao', '-d', required=True,
              help='Descrição do produto')
@click.option('--descricao2', default=None,
              help='Descrição secundária (segunda linha)')
@click.option('--ref', default=None,
              help='Referência do produto (usa codigo se não fornecido)')
@click.option('--pedido', default=None,
              help='Número do pedido')
@click.option('--quantidade', '-q', default=None,
              help='Quantidade')
@click.option('--preco', default=None,
              help='Preço')
@click.option('--codigo-barras', default=None,
              help='Código de barras')
@click.option('--lote', default=None,
              help='Número do lote')
@click.option('--validade', default=None,
              help='Data de validade')
@click.pass_context
def print_label(ctx, printer, codigo, descricao, descricao2, ref, pedido, quantidade, preco, codigo_barras, lote, validade):
    """Imprime uma etiqueta diretamente (sem usar API)."""
    click.echo("[IMPRESSORA] Preparando impressao...\n")
    
    try:
        printer_manager = PrinterManager()
        printer_name = printer_manager.get_printer_name(printer)
        
        if not printer_name:
            click.echo("[ERRO] Nenhuma impressora disponivel.")
            sys.exit(1)
        
        # Prepara dados
        data = {
            "codigo": codigo,
            "descricao": descricao
        }
        
        if descricao2:
            data["descricao2"] = descricao2
        if ref:
            data["ref"] = ref
        if pedido:
            data["pedido"] = pedido
        if quantidade:
            data["quantidade"] = quantidade
        if preco:
            data["preco"] = preco
        if codigo_barras:
            data["codigo_barras"] = codigo_barras
        if lote:
            data["lote"] = lote
        if validade:
            data["validade"] = validade
        
        # Gera ZPL
        zpl_generator = ZPLGenerator()
        zpl = zpl_generator.generate_product_label(data)
        
        click.echo(f"[DADOS] Dados da etiqueta:")
        click.echo(f"   Código: {codigo}")
        click.echo(f"   Descrição: {descricao}")
        if descricao2:
            click.echo(f"   Descrição 2: {descricao2}")
        if ref:
            click.echo(f"   REF: {ref}")
        if pedido:
            click.echo(f"   Pedido: {pedido}")
        if quantidade:
            click.echo(f"   Quantidade: {quantidade}")
        if preco:
            click.echo(f"   Preço: R$ {preco}")
        if codigo_barras:
            click.echo(f"   Código de barras: {codigo_barras}")
        if lote:
            click.echo(f"   Lote: {lote}")
        if validade:
            click.echo(f"   Validade: {validade}")
        click.echo(f"\n[IMPRESSORA] Impressora: {printer_name}")
        click.echo("[ENVIANDO] Enviando para impressao...")
        
        # Imprime
        success = printer_manager.print_zpl(zpl, printer_name)
        
        if success:
            click.echo("[OK] Etiqueta impressa com sucesso!")
        else:
            click.echo("[ERRO] Falha ao imprimir.")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"[ERRO] Erro: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Verifica o status da API."""
    click.echo("[VERIFICANDO] Verificando status da API...\n")
    
    try:
        url = f"{ctx.obj['api_url']}/status"
        headers = get_headers(ctx)
        
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        click.echo("[STATUS] Status da API:")
        click.echo(f"   Status: {data.get('status', 'unknown')}")
        click.echo(f"   Impressora disponivel: {'[OK] Sim' if data.get('printer_available') else '[ERRO] Nao'}")
        
        printer_name = data.get('printer_name')
        if printer_name:
            click.echo(f"   Impressora: {printer_name}")
        
        stats = data.get('queue_stats', {})
        click.echo(f"\n[ESTATISTICAS] Estatisticas da Fila:")
        click.echo(f"   Pendentes: {stats.get('pending', 0)}")
        click.echo(f"   Processando: {stats.get('processing', 0)}")
        click.echo(f"   Concluídas: {stats.get('completed', 0)}")
        click.echo(f"   Falhas: {stats.get('failed', 0)}")
        
    except requests.exceptions.ConnectionError:
        click.echo("[ERRO] Nao foi possivel conectar a API.")
        click.echo(f"   Verifique se a API está rodando em {ctx.obj['api_url']}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        click.echo(f"[ERRO] Erro ao verificar status: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--status-filter', '-s', default=None,
              type=click.Choice(['pending', 'processing', 'completed', 'failed']),
              help='Filtrar por status')
@click.option('--limit', '-l', default=10, type=int,
              help='Número máximo de itens (padrão: 10)')
@click.pass_context
def queue(ctx, status_filter, limit):
    """Visualiza a fila de impressão."""
    click.echo("[FILA] Visualizando fila de impressao...\n")
    
    try:
        url = f"{ctx.obj['api_url']}/queue"
        params = {}
        if status_filter:
            params['status'] = status_filter
        if limit:
            params['limit'] = limit
        
        headers = get_headers(ctx)
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        
        items = response.json()
        
        if not items:
            click.echo("[OK] Fila vazia.")
            return
        
        click.echo(f"[ITENS] Itens na fila ({len(items)}):\n")
        
        for item in items:
            status_icon = {
                'pending': '[PENDENTE]',
                'processing': '[PROCESSANDO]',
                'completed': '[OK]',
                'failed': '[ERRO]'
            }.get(item['status'], '[?]')
            
            click.echo(f"{status_icon} [{item['status'].upper()}] {item['id']}")
            click.echo(f"   Criado em: {item['created_at']}")
            click.echo(f"   Tentativas: {item['attempts']}")
            
            if item.get('error_message'):
                click.echo(f"   Erro: {item['error_message']}")
            
            if item.get('printer_name'):
                click.echo(f"   Impressora: {item['printer_name']}")
            
            click.echo()
        
    except requests.exceptions.ConnectionError:
        click.echo("[ERRO] Nao foi possivel conectar a API.")
        click.echo(f"   Verifique se a API está rodando em {ctx.obj['api_url']}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        click.echo(f"[ERRO] Erro ao visualizar fila: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def process_queue(ctx):
    """Força processamento imediato da fila."""
    click.echo("[PROCESSANDO] Processando fila...\n")
    
    try:
        url = f"{ctx.obj['api_url']}/queue/process"
        headers = get_headers(ctx)
        
        response = requests.post(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        processed = data.get('processed', 0)
        
        click.echo(f"[OK] {processed} requisicao(oes) processada(s).")
        
    except requests.exceptions.ConnectionError:
        click.echo("[ERRO] Nao foi possivel conectar a API.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        click.echo(f"[ERRO] Erro ao processar fila: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--codigo', '-c', required=True,
              help='Código do produto')
@click.option('--descricao', '-d', required=True,
              help='Descrição do produto')
@click.option('--descricao2', default=None,
              help='Descrição secundária (segunda linha)')
@click.option('--ref', default=None,
              help='Referência do produto (usa codigo se não fornecido)')
@click.option('--pedido', default=None,
              help='Número do pedido')
@click.option('--quantidade', '-q', default=None,
              help='Quantidade')
@click.option('--preco', default=None,
              help='Preço')
@click.option('--codigo-barras', default=None,
              help='Código de barras')
@click.option('--lote', default=None,
              help='Número do lote')
@click.option('--validade', default=None,
              help='Data de validade')
@click.option('--printer', '-p', default=None,
              help='Nome da impressora')
@click.pass_context
def print_via_api(ctx, codigo, descricao, descricao2, ref, pedido, quantidade, preco, codigo_barras, lote, validade, printer):
    """Imprime uma etiqueta via API."""
    click.echo("[ENVIANDO] Enviando requisicao de impressao via API...\n")
    
    try:
        url = f"{ctx.obj['api_url']}/print"
        headers = get_headers(ctx)
        
        data = {
            "label_type": "produto",
            "data": {
                "codigo": codigo,
                "descricao": descricao
            }
        }
        
        if descricao2:
            data["data"]["descricao2"] = descricao2
        if ref:
            data["data"]["ref"] = ref
        if pedido:
            data["data"]["pedido"] = pedido
        if quantidade:
            data["data"]["quantidade"] = quantidade
        if preco:
            data["data"]["preco"] = preco
        if codigo_barras:
            data["data"]["codigo_barras"] = codigo_barras
        if lote:
            data["data"]["lote"] = lote
        if validade:
            data["data"]["validade"] = validade
        if printer:
            data["printer_name"] = printer
        
        click.echo(f"[DADOS] Dados:")
        click.echo(f"   Código: {codigo}")
        click.echo(f"   Descrição: {descricao}")
        if descricao2:
            click.echo(f"   Descrição 2: {descricao2}")
        if ref:
            click.echo(f"   REF: {ref}")
        if pedido:
            click.echo(f"   Pedido: {pedido}")
        if quantidade:
            click.echo(f"   Quantidade: {quantidade}")
        if preco:
            click.echo(f"   Preço: R$ {preco}")
        if codigo_barras:
            click.echo(f"   Código de barras: {codigo_barras}")
        if lote:
            click.echo(f"   Lote: {lote}")
        if validade:
            click.echo(f"   Validade: {validade}")
        click.echo()
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('success'):
            click.echo("[OK] Requisicao enviada com sucesso!")
            if result.get('queue_id'):
                click.echo(f"   Queue ID: {result['queue_id']}")
            click.echo(f"   Mensagem: {result.get('message', '')}")
        else:
            click.echo("[ERRO] Falha ao enviar requisicao.")
            sys.exit(1)
        
    except requests.exceptions.ConnectionError:
        click.echo("[ERRO] Nao foi possivel conectar a API.")
        click.echo(f"   Verifique se a API está rodando em {ctx.obj['api_url']}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        click.echo(f"[ERRO] Erro: {e}", err=True)
        if hasattr(e, 'response') and e.response is not None:
            click.echo(f"   Resposta: {e.response.text}")
        sys.exit(1)


@cli.command()
@click.pass_context
def list_printers_api(ctx):
    """Lista impressoras via API."""
    click.echo("[BUSCANDO] Buscando impressoras via API...\n")
    
    try:
        url = f"{ctx.obj['api_url']}/printers"
        headers = get_headers(ctx)
        
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        printers = data.get('printers', [])
        default = data.get('default')
        
        if not printers:
            click.echo("[ERRO] Nenhuma impressora encontrada.")
            return
        
        click.echo(f"[LISTA] Impressoras encontradas ({len(printers)}):\n")
        
        for i, printer in enumerate(printers, 1):
            marker = "[*]" if printer == default else "   "
            click.echo(f"{marker} {i}. {printer}")
            if printer == default:
                click.echo("     (Impressora padrao)")
        
        click.echo(f"\n[OK] Total: {len(printers)} impressora(s)")
        
    except requests.exceptions.ConnectionError:
        click.echo("[ERRO] Nao foi possivel conectar a API.")
        click.echo(f"   Verifique se a API está rodando em {ctx.obj['api_url']}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        click.echo(f"[ERRO] Erro: {e}", err=True)
        sys.exit(1)


@cli.command()
def validate_setup():
    """Valida a configuração do sistema."""
    click.echo("[VALIDANDO] Validando configuracao do sistema...\n")
    
    errors = []
    warnings = []
    
    # Verifica Python
    click.echo("✓ Python detectado")
    
    # Verifica configuração
    try:
        config = get_config()
        click.echo("✓ Arquivo de configuração carregado")
        
        api_key = config.get_api_key()
        if config.is_auth_enabled():
            click.echo("✓ Autenticação habilitada")
        else:
            warnings.append("Autenticação desabilitada (recomendado habilitar)")
        
    except Exception as e:
        errors.append(f"Erro ao carregar configuração: {e}")
    
    # Verifica impressoras
    try:
        printer_manager = PrinterManager()
        printers = printer_manager.list_printers()
        
        if printers:
            click.echo(f"✓ {len(printers)} impressora(s) encontrada(s)")
            default = printer_manager.get_default_printer()
            if default:
                click.echo(f"✓ Impressora padrão: {default}")
        else:
            warnings.append("Nenhuma impressora encontrada no sistema")
    except Exception as e:
        errors.append(f"Erro ao verificar impressoras: {e}")
    
    # Verifica dependências
    try:
        import fastapi
        import uvicorn
        import win32print
        click.echo("✓ Dependências principais instaladas")
    except ImportError as e:
        errors.append(f"Dependência faltando: {e}")
    
    # Resultado
    click.echo()
    
    if warnings:
        click.echo("[AVISO] Avisos:")
        for warning in warnings:
            click.echo(f"   - {warning}")
        click.echo()
    
    if errors:
        click.echo("[ERRO] Erros encontrados:")
        for error in errors:
            click.echo(f"   - {error}")
        click.echo()
        sys.exit(1)
    else:
        click.echo("[OK] Sistema configurado corretamente!")


if __name__ == '__main__':
    cli()

