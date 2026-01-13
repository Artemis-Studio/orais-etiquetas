"""Script para rodar a API diretamente (sem serviço Windows)."""
import logging
from api.main import run_server
from config.config_loader import get_config

if __name__ == "__main__":
    config = get_config()
    
    # Configura logging
    logging.basicConfig(
        level=getattr(logging, config.get_log_level()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.get_log_file()),
            logging.StreamHandler()
        ]
    )
    
    print("Iniciando API de Impressão de Etiquetas...")
    print(f"Servidor rodando em http://{config.get_host()}:{config.get_port()}")
    print("Pressione Ctrl+C para parar")
    
    run_server()

