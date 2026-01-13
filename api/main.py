"""API principal para impressão de etiquetas."""
import logging
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import uvicorn

from .models import PrintRequest, PrintResponse, StatusResponse, QueueItemResponse
from .queue import PrintQueue, QueueStatus
from .printer import PrinterManager
from .zpl_generator import ZPLGenerator
from .queue_processor import QueueProcessor
from config.config_loader import get_config

# Configuração de logging
config = get_config()
logging.basicConfig(
    level=getattr(logging, config.get_log_level()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.get_log_file()),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Inicializa aplicação FastAPI
app = FastAPI(
    title="API de Impressão de Etiquetas",
    description="API REST para impressão de etiquetas Zebra via ZPL",
    version="1.0.0"
)

# Instâncias globais
print_queue = PrintQueue()
printer_manager = PrinterManager(
    default_printer=config.get_default_printer(),
    timeout=config.get_printer_timeout()
)
zpl_generator = ZPLGenerator()
queue_processor = QueueProcessor(print_queue, printer_manager)


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Verifica a API key se autenticação estiver habilitada.
    
    Args:
        x_api_key: API key do header
        
    Returns:
        True se autenticação está OK
        
    Raises:
        HTTPException se autenticação falhar
    """
    if not config.is_auth_enabled():
        return True
    
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key requerida. Forneça no header X-API-Key"
        )
    
    if x_api_key != config.get_api_key():
        raise HTTPException(
            status_code=403,
            detail="API key inválida"
        )
    
    return True


@app.on_event("startup")
async def startup_event():
    """Inicializa componentes quando a API inicia."""
    logger.info("Iniciando API de Impressão de Etiquetas")
    
    # Inicia processador de fila
    queue_processor.start()
    
    logger.info("API iniciada com sucesso")


@app.on_event("shutdown")
async def shutdown_event():
    """Limpa recursos quando a API encerra."""
    logger.info("Encerrando API de Impressão de Etiquetas")
    queue_processor.stop()
    logger.info("API encerrada")


@app.post("/print", response_model=PrintResponse)
async def print_label(
    request: PrintRequest,
    _: bool = Depends(verify_api_key)
):
    """Endpoint para imprimir uma etiqueta.
    
    Args:
        request: Dados da requisição de impressão
        
    Returns:
        Resposta com status da operação
    """
    try:
        # Verifica se impressora está disponível
        printer_name = printer_manager.get_printer_name(request.printer_name)
        printer_available = printer_manager.is_printer_available(printer_name)
        
        # Prepara payload
        payload = {
            "label_type": request.label_type,
            "data": request.data,
            "zpl_template": request.zpl_template
        }
        
        # Tenta imprimir imediatamente se impressora disponível
        if printer_available:
            try:
                # Gera ZPL
                if request.label_type == "produto":
                    zpl = zpl_generator.generate_product_label(request.data)
                else:
                    zpl = zpl_generator.generate_custom_label(
                        request.data, 
                        request.zpl_template
                    )
                
                # Valida ZPL
                if not zpl_generator.validate_zpl(zpl):
                    raise ValueError("Comando ZPL inválido gerado")
                
                # Tenta imprimir
                success = printer_manager.print_zpl(zpl, printer_name)
                
                if success:
                    logger.info(f"Impressão realizada com sucesso: {request.label_type}")
                    return PrintResponse(
                        success=True,
                        message="Impressão realizada com sucesso"
                    )
                else:
                    # Se falhar, adiciona à fila
                    logger.warning("Falha na impressão imediata, adicionando à fila")
            
            except Exception as e:
                logger.warning(f"Erro na impressão imediata: {e}, adicionando à fila")
        
        # Adiciona à fila (se impressora não disponível ou se falhou)
        queue_id = print_queue.add(payload, printer_name)
        logger.info(f"Requisição adicionada à fila: {queue_id}")
        
        return PrintResponse(
            success=True,
            queue_id=queue_id,
            message="Requisição adicionada à fila para processamento"
        )
    
    except Exception as e:
        logger.error(f"Erro ao processar requisição de impressão: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar requisição: {str(e)}"
        )


@app.get("/status", response_model=StatusResponse)
async def get_status(_: bool = Depends(verify_api_key)):
    """Endpoint para verificar status do serviço.
    
    Returns:
        Status do serviço e impressora
    """
    try:
        printer_name = printer_manager.get_printer_name()
        printer_available = printer_manager.is_printer_available()
        queue_stats = print_queue.get_stats()
        
        return StatusResponse(
            status="online",
            printer_available=printer_available,
            printer_name=printer_name,
            queue_stats=queue_stats
        )
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter status: {str(e)}"
        )


@app.get("/queue", response_model=list[QueueItemResponse])
async def get_queue(
    status: Optional[str] = None,
    limit: int = 100,
    _: bool = Depends(verify_api_key)
):
    """Endpoint para visualizar a fila de impressão.
    
    Args:
        status: Filtrar por status (pending, processing, completed, failed)
        limit: Número máximo de itens a retornar
        
    Returns:
        Lista de itens na fila
    """
    try:
        queue_status = None
        if status:
            try:
                queue_status = QueueStatus(status.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Status inválido: {status}. Use: pending, processing, completed, failed"
                )
        
        items = print_queue.get_all(queue_status, limit)
        
        return [
            QueueItemResponse(
                id=item['id'],
                created_at=item['created_at'],
                status=item['status'],
                attempts=item['attempts'],
                error_message=item.get('error_message'),
                printer_name=item.get('printer_name')
            )
            for item in items
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter fila: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter fila: {str(e)}"
        )


@app.post("/queue/process")
async def process_queue(_: bool = Depends(verify_api_key)):
    """Força processamento imediato da fila.
    
    Returns:
        Número de requisições processadas
    """
    try:
        count = queue_processor.process_now()
        return {"success": True, "processed": count, "message": f"{count} requisições processadas"}
    except Exception as e:
        logger.error(f"Erro ao processar fila: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar fila: {str(e)}"
        )


@app.get("/printers")
async def list_printers(_: bool = Depends(verify_api_key)):
    """Lista todas as impressoras disponíveis.
    
    Returns:
        Lista de impressoras
    """
    try:
        printers = printer_manager.list_printers()
        default = printer_manager.get_default_printer()
        
        return {
            "printers": printers,
            "default": default,
            "count": len(printers)
        }
    except Exception as e:
        logger.error(f"Erro ao listar impressoras: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar impressoras: {str(e)}"
        )


@app.get("/")
async def root():
    """Endpoint raiz com informações da API."""
    return {
        "name": "API de Impressão de Etiquetas",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "print": "POST /print - Imprimir etiqueta",
            "status": "GET /status - Status do serviço",
            "queue": "GET /queue - Visualizar fila",
            "printers": "GET /printers - Listar impressoras"
        }
    }


def run_server():
    """Função para rodar o servidor."""
    config_obj = get_config()
    uvicorn.run(
        app,
        host=config_obj.get_host(),
        port=config_obj.get_port(),
        log_level=config_obj.get_log_level().lower()
    )


if __name__ == "__main__":
    run_server()

