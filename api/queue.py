"""Sistema de fila para armazenar requisições de impressão."""
import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from enum import Enum


class QueueStatus(Enum):
    """Status de uma requisição na fila."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PrintQueue:
    """Gerenciador de fila de impressão usando SQLite."""
    
    def __init__(self, db_path: str = "data/print_queue.db"):
        """Inicializa o gerenciador de fila.
        
        Args:
            db_path: Caminho para o banco de dados SQLite
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Inicializa o banco de dados e cria a tabela se não existir."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS print_queue (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                payload TEXT NOT NULL,
                attempts INTEGER DEFAULT 0,
                error_message TEXT,
                printer_name TEXT
            )
        """)
        
        # Índices para melhor performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status 
            ON print_queue(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON print_queue(created_at)
        """)
        
        conn.commit()
        conn.close()
    
    def add(self, payload: Dict, printer_name: Optional[str] = None) -> str:
        """Adiciona uma requisição à fila.
        
        Args:
            payload: Dados da requisição de impressão
            printer_name: Nome da impressora (opcional)
            
        Returns:
            ID único da requisição
        """
        queue_id = str(uuid.uuid4())
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO print_queue (id, status, payload, printer_name)
            VALUES (?, ?, ?, ?)
        """, (
            queue_id,
            QueueStatus.PENDING.value,
            json.dumps(payload, ensure_ascii=False),
            printer_name
        ))
        
        conn.commit()
        conn.close()
        
        return queue_id
    
    def get_pending(self, limit: int = 10) -> List[Dict]:
        """Obtém requisições pendentes.
        
        Args:
            limit: Número máximo de requisições a retornar
            
        Returns:
            Lista de requisições pendentes
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM print_queue
            WHERE status = ?
            ORDER BY created_at ASC
            LIMIT ?
        """, (QueueStatus.PENDING.value, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def get_by_id(self, queue_id: str) -> Optional[Dict]:
        """Obtém uma requisição pelo ID.
        
        Args:
            queue_id: ID da requisição
            
        Returns:
            Dados da requisição ou None se não encontrada
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM print_queue WHERE id = ?", (queue_id,))
        row = cursor.fetchone()
        conn.close()
        
        return self._row_to_dict(row) if row else None
    
    def update_status(self, queue_id: str, status: QueueStatus, 
                     error_message: Optional[str] = None):
        """Atualiza o status de uma requisição.
        
        Args:
            queue_id: ID da requisição
            status: Novo status
            error_message: Mensagem de erro (se houver)
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE print_queue
            SET status = ?,
                updated_at = CURRENT_TIMESTAMP,
                error_message = ?,
                attempts = attempts + 1
            WHERE id = ?
        """, (status.value, error_message, queue_id))
        
        conn.commit()
        conn.close()
    
    def mark_processing(self, queue_id: str):
        """Marca uma requisição como sendo processada."""
        self.update_status(queue_id, QueueStatus.PROCESSING)
    
    def mark_completed(self, queue_id: str):
        """Marca uma requisição como concluída."""
        self.update_status(queue_id, QueueStatus.COMPLETED)
    
    def mark_failed(self, queue_id: str, error_message: str):
        """Marca uma requisição como falha."""
        self.update_status(queue_id, QueueStatus.FAILED, error_message)
    
    def get_all(self, status: Optional[QueueStatus] = None, 
                limit: int = 100) -> List[Dict]:
        """Obtém todas as requisições, opcionalmente filtradas por status.
        
        Args:
            status: Filtrar por status (None para todas)
            limit: Número máximo de requisições
            
        Returns:
            Lista de requisições
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT * FROM print_queue
                WHERE status = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (status.value, limit))
        else:
            cursor.execute("""
                SELECT * FROM print_queue
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas da fila.
        
        Returns:
            Dicionário com estatísticas
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM print_queue
            GROUP BY status
        """)
        
        stats = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        
        return {
            'pending': stats.get(QueueStatus.PENDING.value, 0),
            'processing': stats.get(QueueStatus.PROCESSING.value, 0),
            'completed': stats.get(QueueStatus.COMPLETED.value, 0),
            'failed': stats.get(QueueStatus.FAILED.value, 0),
        }
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Converte uma linha do banco em dicionário."""
        return {
            'id': row['id'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'status': row['status'],
            'payload': json.loads(row['payload']),
            'attempts': row['attempts'],
            'error_message': row['error_message'],
            'printer_name': row['printer_name']
        }

