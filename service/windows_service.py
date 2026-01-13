"""Serviço Windows para rodar a API sempre ativa."""
import sys
import os
import time
import logging
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

import win32serviceutil
import win32service
import servicemanager
import uvicorn
from threading import Thread

from api.main import app
from config.config_loader import get_config

logger = logging.getLogger(__name__)


class LabelPrintingService(win32serviceutil.ServiceFramework):
    """Serviço Windows para API de Impressão de Etiquetas."""
    
    _svc_name_ = "LabelPrintingAPI"
    _svc_display_name_ = "API de Impressão de Etiquetas"
    _svc_description_ = "Serviço para impressão de etiquetas via API REST"
    
    def __init__(self, args):
        """Inicializa o serviço."""
        win32serviceutil.ServiceFramework.__init__(self, args)
        import threading
        self.stop_event = threading.Event()
        self.server_thread = None
        self.server = None
        self.config = get_config()
    
    def SvcStop(self):
        """Para o serviço."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        servicemanager.LogInfoMsg("Parando serviço de impressão de etiquetas...")
        
        # Para o servidor uvicorn
        if self.server:
            self.server.should_exit = True
        
        # Sinaliza para parar
        self.stop_event.set()
        
        # Aguarda thread terminar
        if self.server_thread:
            self.server_thread.join(timeout=5)
        
        servicemanager.LogInfoMsg("Serviço parado")
    
    def SvcDoRun(self):
        """Executa o serviço."""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        servicemanager.LogInfoMsg("Iniciando serviço de impressão de etiquetas...")
        
        try:
            # Configura logging
            logging.basicConfig(
                level=getattr(logging, self.config.get_log_level()),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(self.config.get_log_file()),
                    logging.StreamHandler()
                ]
            )
            
            # Inicia servidor em thread separada
            self.server_thread = Thread(
                target=self._run_server,
                daemon=False
            )
            self.server_thread.start()
            
            # Mantém serviço rodando
            servicemanager.LogInfoMsg("Serviço iniciado com sucesso")
            
            # Aguarda até receber sinal de parada
            while True:
                time.sleep(1)
                if self.stop_event and self.stop_event.is_set():
                    break
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"Erro no serviço: {e}")
            raise
    
    def _run_server(self):
        """Roda o servidor uvicorn."""
        try:
            config = get_config()
            servicemanager.LogInfoMsg(
                f"Iniciando servidor em {config.get_host()}:{config.get_port()}"
            )
            
            # Configura uvicorn
            config_uvicorn = uvicorn.Config(
                app,
                host=config.get_host(),
                port=config.get_port(),
                log_level=config.get_log_level().lower(),
                access_log=True
            )
            
            self.server = uvicorn.Server(config_uvicorn)
            self.server.run()
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"Erro ao iniciar servidor: {e}")
            raise


def main():
    """Função principal para instalar/desinstalar/rodar o serviço."""
    if len(sys.argv) == 1:
        # Se rodado sem argumentos, tenta rodar como serviço
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(LabelPrintingService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Usa win32serviceutil para instalar/desinstalar
        win32serviceutil.HandleCommandLine(LabelPrintingService)


if __name__ == '__main__':
    main()

