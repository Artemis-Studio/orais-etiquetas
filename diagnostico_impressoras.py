"""Script de diagnóstico para verificar acesso a impressoras."""
import sys
import win32print
import win32api
from pathlib import Path

# Configura encoding UTF-8 para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent))

from api.printer import PrinterManager


def diagnostico_completo():
    """Executa diagnóstico completo de impressoras."""
    print("=" * 70)
    print("DIAGNÓSTICO DE IMPRESSORAS")
    print("=" * 70)
    print()
    
    # Informações do usuário
    print("[1] Informações do Usuário:")
    print(f"    Usuário atual: {win32api.GetUserName()}")
    print(f"    Computador: {win32api.GetComputerName()}")
    print()
    
    # Lista impressoras usando diferentes métodos
    print("[2] Buscando impressoras...")
    print()
    
    printer_manager = PrinterManager()
    
    # Impressoras locais
    print("    [2.1] Impressoras LOCAIS:")
    try:
        local_printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
        if local_printers:
            for printer in local_printers:
                print(f"        ✓ {printer[2]}")
        else:
            print("        ✗ Nenhuma impressora local encontrada")
    except Exception as e:
        print(f"        ✗ Erro: {e}")
    print()
    
    # Impressoras conectadas (conexões anteriores)
    print("    [2.2] Impressoras CONECTADAS (conexões anteriores):")
    try:
        connected_printers = win32print.EnumPrinters(4)  # PRINTER_ENUM_CONNECTIONS = 4
        if connected_printers:
            for printer in connected_printers:
                print(f"        ✓ {printer[2]}")
        else:
            print("        ✗ Nenhuma impressora conectada encontrada")
    except Exception as e:
        print(f"        ✗ Erro (pode ser normal): {e}")
    print()
    
    # Impressoras compartilhadas
    print("    [2.3] Impressoras COMPARTILHADAS:")
    try:
        shared_printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_SHARED)
        if shared_printers:
            for printer in shared_printers:
                print(f"        ✓ {printer[2]}")
        else:
            print("        ✗ Nenhuma impressora compartilhada encontrada")
    except Exception as e:
        print(f"        ✗ Erro (pode ser normal se não houver acesso): {e}")
    print()
    
    # Impressora padrão
    print("[3] Impressora Padrão:")
    try:
        default = printer_manager.get_default_printer()
        if default:
            print(f"    ✓ {default}")
        else:
            print("    ✗ Nenhuma impressora padrão configurada")
    except Exception as e:
        print(f"    ✗ Erro: {e}")
    print()
    
    # Lista usando PrinterManager (método atualizado)
    print("[4] Lista usando PrinterManager (método atualizado):")
    printers = printer_manager.list_printers()
    if printers:
        print(f"    ✓ {len(printers)} impressora(s) encontrada(s):")
        for printer in printers:
            marker = " [PADRÃO]" if printer == printer_manager.get_default_printer() else ""
            print(f"        - {printer}{marker}")
    else:
        print("    ✗ Nenhuma impressora encontrada")
    print()
    
    # Diagnóstico e recomendações
    print("=" * 70)
    print("DIAGNÓSTICO:")
    print("=" * 70)
    
    if not printers:
        print()
        print("⚠️  PROBLEMA: Nenhuma impressora encontrada!")
        print()
        print("Possíveis causas:")
        print("  1. Usuário atual não tem acesso às impressoras")
        print("  2. Impressoras não estão instaladas para este usuário")
        print("  3. Serviço de impressão do Windows não está rodando")
        print()
        print("SOLUÇÕES:")
        print("  1. Instalar a impressora para este usuário:")
        print("     - Abra 'Configurações' > 'Impressoras e scanners'")
        print("     - Clique em 'Adicionar impressora ou scanner'")
        print("     - Siga o assistente de instalação")
        print()
        print("  2. Se a impressora está instalada em outro usuário:")
        print("     - Faça login com o usuário que tem a impressora")
        print("     - Compartilhe a impressora")
        print("     - Ou instale a impressora novamente para este usuário")
        print()
        print("  3. Executar como Administrador:")
        print("     - Execute este script como Administrador")
        print("     - Isso pode dar acesso a mais impressoras")
        print()
        print("  4. Verificar se o serviço de impressão está rodando:")
        print("     - Abra 'Serviços' (services.msc)")
        print("     - Verifique se 'Spooler de Impressão' está rodando")
    else:
        print()
        print("✅ Impressoras encontradas com sucesso!")
        print(f"   Total: {len(printers)} impressora(s)")
        if printer_manager.get_default_printer():
            print(f"   Padrão: {printer_manager.get_default_printer()}")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    try:
        diagnostico_completo()
    except Exception as e:
        print(f"\n❌ Erro durante diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
