import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    """Classe para gerenciar todas as operações do banco de dados."""
    
    def __init__(self, db_path: str = 'diario_bordo.db'):
        """
        Inicializa o gerenciador do banco de dados.
        
        Args:
            db_path: Caminho para o arquivo do banco de dados SQLite
        """
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Cria o banco de dados e as tabelas se não existirem."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Executa o schema SQL
            cursor.executescript('''
                CREATE TABLE IF NOT EXISTS viagens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    hora_saida TEXT NOT NULL,
                    km_inicial INTEGER NOT NULL,
                    destino TEXT NOT NULL,
                    hora_chegada TEXT,
                    km_final INTEGER,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TRIGGER IF NOT EXISTS atualiza_timestamp
                AFTER UPDATE ON viagens
                FOR EACH ROW
                BEGIN
                    UPDATE viagens SET atualizado_em = CURRENT_TIMESTAMP WHERE id = OLD.id;
                END;
            ''')
            conn.commit()

    def _get_connection(self):
        """Retorna uma conexão com o banco de dados."""
        return sqlite3.connect(self.db_path)

    def iniciar_viagem(self, data: str, hora_saida: str, km_inicial: int, destino: str) -> int:
        """
        Registra uma nova viagem no banco de dados.
        
        Args:
            data: Data no formato DD/MM/YYYY
            hora_saida: Hora no formato HH:MM
            km_inicial: Quilometragem inicial
            destino: Destino da viagem
            
        Returns:
            ID da viagem criada
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO viagens (data, hora_saida, km_inicial, destino)
                VALUES (?, ?, ?, ?)
                ''',
                (data, hora_saida, km_inicial, destino)
            )
            conn.commit()
            return cursor.lastrowid

    def finalizar_viagem(self, viagem_id: int, hora_chegada: str, km_final: int) -> bool:
        """
        Finaliza uma viagem existente.
        
        Args:
            viagem_id: ID da viagem a ser finalizada
            hora_chegada: Hora de chegada no formato HH:MM
            km_final: Quilometragem final
            
        Returns:
            True se a operação foi bem-sucedida
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                UPDATE viagens
                SET hora_chegada = ?, km_final = ?
                WHERE id = ?
                ''',
                (hora_chegada, km_final, viagem_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def obter_viagens(self) -> List[Dict]:
        """
        Retorna todas as viagens registradas.
        
        Returns:
            Lista de dicionários com informações das viagens
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM viagens ORDER BY data DESC, hora_saida DESC')
            return [dict(row) for row in cursor.fetchall()]

    def obter_viagem_ativa(self) -> Optional[Dict]:
        """
        Retorna a última viagem não finalizada, se existir.
        
        Returns:
            Dicionário com informações da viagem ou None se não houver viagem ativa
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT * FROM viagens
                WHERE hora_chegada IS NULL
                ORDER BY data DESC, hora_saida DESC
                LIMIT 1
                '''
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def atualizar_viagem(self, viagem_id: int, **kwargs) -> bool:
        """
        Atualiza informações de uma viagem.
        
        Args:
            viagem_id: ID da viagem a ser atualizada
            kwargs: Campos a serem atualizados (data, hora_saida, km_inicial, etc.)
            
        Returns:
            True se a operação foi bem-sucedida
        """
        if not kwargs:
            return False
            
        set_clause = ', '.join(f"{key} = ?" for key in kwargs.keys())
        values = list(kwargs.values())
        values.append(viagem_id)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f'''
                UPDATE viagens
                SET {set_clause}
                WHERE id = ?
                ''',
                values
            )
            conn.commit()
            return cursor.rowcount > 0