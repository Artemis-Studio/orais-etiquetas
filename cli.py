"""CLI para gerenciamento e validação da API de Impressão de Etiquetas."""
import click
import requests
import json
import sys
from typing import Optional
from pathlib import Path

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
    click.echo("🔍 Buscando impressoras disponíveis...\n")
    
    try:
        # Usa a biblioteca diretamente para listar impressoras locais
        printer_manager = PrinterManager()
        printers = printer_manager.list_printers()
        default = printer_manager.get_default_printer()
        
        if not printers:
            click.echo("❌ Nenhuma impressora encontrada no sistema.")
            return
        
        click.echo(f"📋 Impressoras encontradas ({len(printers)}):\n")
        
        for i, printer in enumerate(printers, 1):
            marker = "⭐" if printer == default else "  "
            click.echo(f"{marker} {i}. {printer}")
            if printer == default:
                click.echo("     (Impressora padrão do sistema)")
        
        click.echo(f"\n✅ Total: {len(printers)} impressora(s)")
        
    except Exception as e:
        click.echo(f"❌ Erro ao listar impressoras: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--printer', '-p', default=None, 
              help='Nome da impressora (deixe vazio para usar padrão)')
@click.pass_context
def test_printer(ctx, printer):
    """Testa a impressão em uma impressora."""
    click.echo("🧪 Testando impressão...\n")
    
    try:
        printer_manager = PrinterManager()
        printer_name = printer_manager.get_printer_name(printer)
        
        if not printer_name:
            click.echo("❌ Nenhuma impressora disponível.")
            sys.exit(1)
        
        click.echo(f"🖨️  Impressora: {printer_name}")
        click.echo("📄 Enviando etiqueta de teste...")
        
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
            click.echo("✅ Impressão de teste enviada com sucesso!")
            click.echo(f"   Verifique a impressora: {printer_name}")
        else:
            click.echo("❌ Falha ao enviar impressão.")
            click.echo("   Verifique se a impressora está ligada e conectada.")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Erro ao testar impressão: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--printer', '-p', default=None,
              help='Nome da impressora')
@click.option('--codigo', '-c', required=True,
              help='Código do produto')
@click.option('--descricao', '-d', required=True,
              help='Descrição do produto')
@click.option('--quantidade', '-q', default=None,
              help='Quantidade')
@click.option('--preco', default=None,
              help='Preço')
@click.option('--codigo-barras', default=None,
              help='Código de barras')
@click.pass_context
def print_label(ctx, printer, codigo, descricao, quantidade, preco, codigo_barras):
    """Imprime uma etiqueta diretamente (sem usar API)."""
    click.echo("🖨️  Preparando impressão...\n")
    
    try:
        printer_manager = PrinterManager()
        printer_name = printer_manager.get_printer_name(printer)
        
        if not printer_name:
            click.echo("❌ Nenhuma impressora disponível.")
            sys.exit(1)
        
        # Prepara dados
        data = {
            "codigo": codigo,
            "descricao": descricao
        }
        
        if quantidade:
            data["quantidade"] = quantidade
        if preco:
            data["preco"] = preco
        if codigo_barras:
            data["codigo_barras"] = codigo_barras
        
        # Gera ZPL
        zpl_generator = ZPLGenerator()
        zpl = zpl_generator.generate_product_label(data)
        
        click.echo(f"📋 Dados da etiqueta:")
        click.echo(f"   Código: {codigo}")
        click.echo(f"   Descrição: {descricao}")
        if quantidade:
            click.echo(f"   Quantidade: {quantidade}")
        if preco:
            click.echo(f"   Preço: R$ {preco}")
        click.echo(f"\n🖨️  Impressora: {printer_name}")
        click.echo("📄 Enviando para impressão...")
        
        # Imprime
        success = printer_manager.print_zpl(zpl, printer_name)
        
        if success:
            click.echo("✅ Etiqueta impressa com sucesso!")
        else:
            click.echo("❌ Falha ao imprimir.")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Erro: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Verifica o status da API."""
    click.echo("🔍 Verificando status da API...\n")
    
    try:
        url = f"{ctx.obj['api_url']}/status"
        headers = get_headers(ctx)
        
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        click.echo("📊 Status da API:")
        click.echo(f"   Status: {data.get('status', 'unknown')}")
        click.echo(f"   Impressora disponível: {'✅ Sim' if data.get('printer_available') else '❌ Não'}")
        
        printer_name = data.get('printer_name')
        if printer_name:
            click.echo(f"   Impressora: {printer_name}")
        
        stats = data.get('queue_stats', {})
        click.echo(f"\n📋 Estatísticas da Fila:")
        click.echo(f"   Pendentes: {stats.get('pending', 0)}")
        click.echo(f"   Processando: {stats.get('processing', 0)}")
        click.echo(f"   Concluídas: {stats.get('completed', 0)}")
        click.echo(f"   Falhas: {stats.get('failed', 0)}")
        
    except requests.exceptions.ConnectionError:
        click.echo("❌ Não foi possível conectar à API.")
        click.echo(f"   Verifique se a API está rodando em {ctx.obj['api_url']}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Erro ao verificar status: {e}", err=True)
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
    click.echo("📋 Visualizando fila de impressão...\n")
    
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
            click.echo("✅ Fila vazia.")
            return
        
        click.echo(f"📊 Itens na fila ({len(items)}):\n")
        
        for item in items:
            status_icon = {
                'pending': '⏳',
                'processing': '🔄',
                'completed': '✅',
                'failed': '❌'
            }.get(item['status'], '❓')
            
            click.echo(f"{status_icon} [{item['status'].upper()}] {item['id']}")
            click.echo(f"   Criado em: {item['created_at']}")
            click.echo(f"   Tentativas: {item['attempts']}")
            
            if item.get('error_message'):
                click.echo(f"   Erro: {item['error_message']}")
            
            if item.get('printer_name'):
                click.echo(f"   Impressora: {item['printer_name']}")
            
            click.echo()
        
    except requests.exceptions.ConnectionError:
        click.echo("❌ Não foi possível conectar à API.")
        click.echo(f"   Verifique se a API está rodando em {ctx.obj['api_url']}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Erro ao visualizar fila: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def process_queue(ctx):
    """Força processamento imediato da fila."""
    click.echo("🔄 Processando fila...\n")
    
    try:
        url = f"{ctx.obj['api_url']}/queue/process"
        headers = get_headers(ctx)
        
        response = requests.post(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        processed = data.get('processed', 0)
        
        click.echo(f"✅ {processed} requisição(ões) processada(s).")
        
    except requests.exceptions.ConnectionError:
        click.echo("❌ Não foi possível conectar à API.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Erro ao processar fila: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--codigo', '-c', required=True,
              help='Código do produto')
@click.option('--descricao', '-d', required=True,
              help='Descrição do produto')
@click.option('--quantidade', '-q', default=None,
              help='Quantidade')
@click.option('--preco', default=None,
              help='Preço')
@click.option('--printer', '-p', default=None,
              help='Nome da impressora')
@click.pass_context
def print_via_api(ctx, codigo, descricao, quantidade, preco, printer):
    """Imprime uma etiqueta via API."""
    click.echo("🖨️  Enviando requisição de impressão via API...\n")
    
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
        
        if quantidade:
            data["data"]["quantidade"] = quantidade
        if preco:
            data["data"]["preco"] = preco
        if printer:
            data["printer_name"] = printer
        
        click.echo(f"📋 Dados:")
        click.echo(f"   Código: {codigo}")
        click.echo(f"   Descrição: {descricao}")
        if quantidade:
            click.echo(f"   Quantidade: {quantidade}")
        if preco:
            click.echo(f"   Preço: R$ {preco}")
        click.echo()
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('success'):
            click.echo("✅ Requisição enviada com sucesso!")
            if result.get('queue_id'):
                click.echo(f"   Queue ID: {result['queue_id']}")
            click.echo(f"   Mensagem: {result.get('message', '')}")
        else:
            click.echo("❌ Falha ao enviar requisição.")
            sys.exit(1)
        
    except requests.exceptions.ConnectionError:
        click.echo("❌ Não foi possível conectar à API.")
        click.echo(f"   Verifique se a API está rodando em {ctx.obj['api_url']}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Erro: {e}", err=True)
        if hasattr(e, 'response') and e.response is not None:
            click.echo(f"   Resposta: {e.response.text}")
        sys.exit(1)


@cli.command()
@click.pass_context
def list_printers_api(ctx):
    """Lista impressoras via API."""
    click.echo("🔍 Buscando impressoras via API...\n")
    
    try:
        url = f"{ctx.obj['api_url']}/printers"
        headers = get_headers(ctx)
        
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        printers = data.get('printers', [])
        default = data.get('default')
        
        if not printers:
            click.echo("❌ Nenhuma impressora encontrada.")
            return
        
        click.echo(f"📋 Impressoras encontradas ({len(printers)}):\n")
        
        for i, printer in enumerate(printers, 1):
            marker = "⭐" if printer == default else "  "
            click.echo(f"{marker} {i}. {printer}")
            if printer == default:
                click.echo("     (Impressora padrão)")
        
        click.echo(f"\n✅ Total: {len(printers)} impressora(s)")
        
    except requests.exceptions.ConnectionError:
        click.echo("❌ Não foi possível conectar à API.")
        click.echo(f"   Verifique se a API está rodando em {ctx.obj['api_url']}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Erro: {e}", err=True)
        sys.exit(1)


@cli.command()
def validate_setup():
    """Valida a configuração do sistema."""
    click.echo("🔍 Validando configuração do sistema...\n")
    
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
        click.echo("⚠️  Avisos:")
        for warning in warnings:
            click.echo(f"   - {warning}")
        click.echo()
    
    if errors:
        click.echo("❌ Erros encontrados:")
        for error in errors:
            click.echo(f"   - {error}")
        click.echo()
        sys.exit(1)
    else:
        click.echo("✅ Sistema configurado corretamente!")


if __name__ == '__main__':
    cli()

