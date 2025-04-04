"""
Pacote database - Gerencia a persistência de dados do Diário de Bordo

Exporta a classe DatabaseManager para uso externo e realiza configurações iniciais.
"""

from .database import DatabaseManager

__all__ = ['DatabaseManager']

# Configurações iniciais (opcional)
DEFAULT_DB_PATH = 'data/diario_bordo.db'


def init_db(db_path: str = DEFAULT_DB_PATH):
    """
    Inicializa o banco de dados com as tabelas necessárias.

    Args:
        db_path: Caminho para o arquivo do banco de dados
    """
    db = DatabaseManager(db_path)
    return db


# Cria uma instância global (opcional)
db_manager = DatabaseManager(DEFAULT_DB_PATH)