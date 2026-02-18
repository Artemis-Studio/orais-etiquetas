"""Processador de fila que processa requisições pendentes automaticamente."""
import threading
import time
import logging
from typing import Optional
from .queue import PrintQueue, QueueStatus
from .printer import PrinterManager
from .zpl_generator import ZPLGenerator
from config.config_loader import get_config

logger = logging.getLogger(__name__)


class QueueProcessor:
    """Processa requisições pendentes na fila automaticamente."""
    
    def __init__(self, print_queue: PrintQueue, printer_manager: PrinterManager):
        """Inicializa o processador de fila.
        
        Args:
            print_queue: Instância do gerenciador de fila
            printer_manager: Instância do gerenciador de impressão
        """
        self.print_queue = print_queue
        self.printer_manager = printer_manager
        self.zpl_generator = ZPLGenerator()
        self.config = get_config()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.check_interval = self.config.get_queue_check_interval()
        self.max_retries = self.config.get_max_retries()
    
    def start(self):
        """Inicia o processador em uma thread separada."""
        if self.running:
            logger.warning("Processador de fila já está rodando")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.thread.start()
        logger.info("Processador de fila iniciado")
    
    def stop(self):
        """Para o processador."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Processador de fila parado")
    
    def _process_loop(self):
        """Loop principal de processamento."""
        while self.running:
            try:
                self._process_pending()
            except Exception as e:
                logger.error(f"Erro no processamento da fila: {e}")
            
            # Aguarda antes da próxima verificação
            time.sleep(self.check_interval)
    
    def _process_pending(self):
        """Processa requisições pendentes."""
        # Obtém requisições pendentes
        pending = self.print_queue.get_pending(limit=10)
        
        if not pending:
            return
        
        logger.info(f"Processando {len(pending)} requisições pendentes")
        
        for item in pending:
            if not self.running:
                break
            
            queue_id = item['id']
            payload = item['payload']
            printer_name = item.get('printer_name')
            
            # Marca como processando
            self.print_queue.mark_processing(queue_id)
            
            try:
                # Processa a impressão
                success = self._process_print_request(payload, printer_name)
                
                if success:
                    self.print_queue.mark_completed(queue_id)
                    logger.info(f"Requisição {queue_id} processada com sucesso")
                else:
                    # Verifica se excedeu tentativas
                    attempts = item.get('attempts', 0) + 1
                    if attempts >= self.max_retries:
                        self.print_queue.mark_failed(
                            queue_id, 
                            f"Falha após {attempts} tentativas"
                        )
                        logger.error(f"Requisição {queue_id} falhou após {attempts} tentativas")
                    else:
                        # Volta para pendente para nova tentativa
                        self.print_queue.update_status(queue_id, QueueStatus.PENDING)
                        logger.warning(f"Requisição {queue_id} falhou, será tentada novamente")
            
            except Exception as e:
                error_msg = str(e)
                attempts = item.get('attempts', 0) + 1
                
                if attempts >= self.max_retries:
                    self.print_queue.mark_failed(queue_id, error_msg)
                    logger.error(f"Erro ao processar {queue_id}: {error_msg}")
                else:
                    self.print_queue.update_status(queue_id, QueueStatus.PENDING, error_msg)
                    logger.warning(f"Erro ao processar {queue_id}, será tentado novamente: {error_msg}")
    
    def _process_print_request(self, payload: dict, printer_name: Optional[str] = None) -> bool:
        """Processa uma requisição de impressão individual.
        
        Args:
            payload: Dados da requisição
            printer_name: Nome da impressora (opcional)
            
        Returns:
            True se impressão foi bem-sucedida
        """
        # Verifica se impressora está disponível
        if not self.printer_manager.is_printer_available(printer_name):
            logger.warning(f"Impressora não disponível: {printer_name or 'padrão'}")
            return False
        
        # Extrai tipo de etiqueta e dados
        label_type = payload.get('label_type', 'produto')
        data = payload.get('data', {})
        
        # Gera comando ZPL
        if label_type == 'produto':
            if payload.get('duas_colunas'):
                data_col2 = payload.get('data_col2') or data
                zpl = self.zpl_generator.generate_dual_column_label(data, data_col2)
            else:
                zpl = self.zpl_generator.generate_product_label(data)
        else:
            # Usa template customizado se fornecido
            template = payload.get('zpl_template')
            zpl = self.zpl_generator.generate_custom_label(data, template)
        
        # Valida ZPL
        if not self.zpl_generator.validate_zpl(zpl):
            logger.error("Comando ZPL inválido gerado")
            return False
        
        # Envia para impressora
        return self.printer_manager.print_zpl(zpl, printer_name)
    
    def process_now(self) -> int:
        """Força processamento imediato da fila.
        
        Returns:
            Número de requisições processadas
        """
        count = 0
        pending = self.print_queue.get_pending(limit=50)
        
        for item in pending:
            queue_id = item['id']
            payload = item['payload']
            printer_name = item.get('printer_name')
            
            self.print_queue.mark_processing(queue_id)
            
            try:
                if self._process_print_request(payload, printer_name):
                    self.print_queue.mark_completed(queue_id)
                    count += 1
                else:
                    attempts = item.get('attempts', 0) + 1
                    if attempts >= self.max_retries:
                        self.print_queue.mark_failed(queue_id, "Falha na impressão")
                    else:
                        self.print_queue.update_status(queue_id, QueueStatus.PENDING)
            except Exception as e:
                self.print_queue.mark_failed(queue_id, str(e))
        
        return count

