"""Integração com impressora Zebra."""
import win32print
import win32api
import time
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class PrinterManager:
    """Gerenciador de impressão para impressoras Zebra."""
    
    def __init__(self, default_printer: Optional[str] = None, timeout: int = 30):
        """Inicializa o gerenciador de impressão.
        
        Args:
            default_printer: Nome da impressora padrão (None para usar a primeira disponível)
            timeout: Timeout em segundos para operações de impressão
        """
        self.default_printer = default_printer
        self.timeout = timeout
    
    def list_printers(self) -> List[str]:
        """Lista todas as impressoras disponíveis.
        
        Busca impressoras locais, compartilhadas e conectadas.
        
        Returns:
            Lista com nomes das impressoras
        """
        try:
            printers = []
            printer_names = set()  # Usa set para evitar duplicatas
            
            # Tenta listar impressoras locais
            try:
                printer_info = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
                for printer in printer_info:
                    printer_names.add(printer[2])  # Nome da impressora
            except Exception as e:
                logger.warning(f"Erro ao listar impressoras locais: {e}")
            
            # Tenta listar impressoras conectadas
            try:
                printer_info = win32print.EnumPrinters(win32print.PRINTER_ENUM_CONNECTED)
                for printer in printer_info:
                    printer_names.add(printer[2])
            except Exception as e:
                logger.warning(f"Erro ao listar impressoras conectadas: {e}")
            
            # Tenta listar impressoras compartilhadas (pode não ter acesso)
            try:
                printer_info = win32print.EnumPrinters(win32print.PRINTER_ENUM_SHARED)
                for printer in printer_info:
                    printer_names.add(printer[2])
            except Exception as e:
                logger.debug(f"Erro ao listar impressoras compartilhadas (pode ser normal): {e}")
            
            return sorted(list(printer_names))
        except Exception as e:
            logger.error(f"Erro ao listar impressoras: {e}")
            return []
    
    def get_default_printer(self) -> Optional[str]:
        """Obtém a impressora padrão do sistema.
        
        Returns:
            Nome da impressora padrão ou None
        """
        try:
            return win32print.GetDefaultPrinter()
        except Exception as e:
            logger.error(f"Erro ao obter impressora padrão: {e}")
            return None
    
    def get_printer_name(self, printer_name: Optional[str] = None) -> Optional[str]:
        """Obtém o nome da impressora a usar.
        
        Args:
            printer_name: Nome específico da impressora (opcional)
            
        Returns:
            Nome da impressora a usar ou None se não encontrada
        """
        if printer_name:
            # Verifica se a impressora existe
            printers = self.list_printers()
            if printer_name in printers:
                return printer_name
            else:
                logger.warning(f"Impressora '{printer_name}' não encontrada")
        
        # Usa impressora padrão configurada
        if self.default_printer:
            printers = self.list_printers()
            if self.default_printer in printers:
                return self.default_printer
        
        # Usa impressora padrão do sistema
        return self.get_default_printer()
    
    def print_zpl(self, zpl_command: str, printer_name: Optional[str] = None) -> bool:
        """Imprime um comando ZPL na impressora especificada.
        
        Args:
            zpl_command: Comando ZPL completo
            printer_name: Nome da impressora (opcional)
            
        Returns:
            True se impressão foi bem-sucedida, False caso contrário
        """
        printer = self.get_printer_name(printer_name)
        
        if not printer:
            logger.error("Nenhuma impressora disponível")
            return False
        
        try:
            # Abre a impressora
            hprinter = win32print.OpenPrinter(printer)
            
            try:
                # Inicia documento de impressão
                job_info = ("Etiqueta", None, "RAW")
                job_id = win32print.StartDocPrinter(hprinter, 1, job_info)
                
                try:
                    win32print.StartPagePrinter(hprinter)
                    
                    # Envia comando ZPL
                    # ZPL precisa ser enviado como bytes
                    zpl_bytes = zpl_command.encode('utf-8')
                    win32print.WritePrinter(hprinter, zpl_bytes)
                    
                    win32print.EndPagePrinter(hprinter)
                    
                finally:
                    win32print.EndDocPrinter(hprinter)
                
                logger.info(f"Impressão enviada com sucesso para {printer} (Job ID: {job_id})")
                return True
                
            finally:
                win32print.ClosePrinter(hprinter)
                
        except Exception as e:
            logger.error(f"Erro ao imprimir: {e}")
            return False
    
    def is_printer_available(self, printer_name: Optional[str] = None) -> bool:
        """Verifica se a impressora está disponível.
        
        Args:
            printer_name: Nome da impressora (opcional)
            
        Returns:
            True se disponível, False caso contrário
        """
        printer = self.get_printer_name(printer_name)
        if not printer:
            return False
        
        try:
            printers = self.list_printers()
            return printer in printers
        except Exception:
            return False
    
    def test_print(self, printer_name: Optional[str] = None) -> bool:
        """Envia uma impressão de teste.
        
        Args:
            printer_name: Nome da impressora (opcional)
            
        Returns:
            True se teste foi bem-sucedido
        """
        test_zpl = """
^XA
^FO50,50^A0N,50,50^FDTESTE DE IMPRESSAO^FS
^FO50,120^BY3^BCN,60,Y,N,N^FD123456789^FS
^XZ
"""
        return self.print_zpl(test_zpl, printer_name)

