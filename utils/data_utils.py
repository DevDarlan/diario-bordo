"""
Módulo de utilitários para manipulação de dados, datas e validações.
"""

from datetime import datetime
from typing import Optional, Tuple, Union
import re

class DataUtils:
    """Classe com métodos utilitários para manipulação de datas e validações."""
    
    # Formatos constantes
    FORMATO_DATA = '%d/%m/%Y'
    FORMATO_HORA = '%H:%M'
    FORMATO_DATA_HORA = f'{FORMATO_DATA} {FORMATO_HORA}'
    
    @classmethod
    def validar_data(cls, data: str) -> bool:
        """Valida se uma string está no formato DD/MM/YYYY."""
        try:
            datetime.strptime(data, cls.FORMATO_DATA)
            return True
        except ValueError:
            return False
    
    @classmethod
    def validar_hora(cls, hora: str) -> bool:
        """Valida se uma string está no formato HH:MM."""
        try:
            datetime.strptime(hora, cls.FORMATO_HORA)
            return True
        except ValueError:
            return False
    
    @classmethod
    def validar_data_hora(cls, data: str, hora: str) -> Tuple[bool, Optional[datetime]]:
        """Valida e combina data e hora em um objeto datetime."""
        try:
            data_hora = datetime.strptime(f"{data} {hora}", cls.FORMATO_DATA_HORA)
            return True, data_hora
        except ValueError:
            return False, None
    
    @classmethod
    def formatar_data(cls, data: datetime) -> str:
        """Formata datetime para string DD/MM/YYYY."""
        return data.strftime(cls.FORMATO_DATA)
    
    @classmethod
    def formatar_hora(cls, hora: datetime) -> str:
        """Formata datetime para string HH:MM."""
        return hora.strftime(cls.FORMATO_HORA)
    
    @classmethod
    def calcular_duracao(cls, inicio: datetime, fim: datetime) -> str:
        """Calcula diferença entre dois datetimes no formato HH:MM."""
        if not inicio or not fim:
            return "N/A"
        
        diferenca = fim - inicio
        horas, resto = divmod(diferenca.seconds, 3600)
        minutos = resto // 60
        return f"{horas:02d}:{minutos:02d}"
    
    @classmethod
    def hoje_formatado(cls) -> str:
        """Retorna a data atual formatada."""
        return datetime.now().strftime(cls.FORMATO_DATA)
    
    @classmethod
    def hora_atual_formatada(cls) -> str:
        """Retorna a hora atual formatada."""
        return datetime.now().strftime(cls.FORMATO_HORA)


class Validador:
    """Classe para validação de dados de negócio."""
    
    @staticmethod
    def validar_km(km: Union[int, float, str]) -> Tuple[bool, Optional[int]]:
        """Valida se o KM é um número positivo."""
        try:
            km_int = int(km)
            return (True, km_int) if km_int >= 0 else (False, None)
        except (ValueError, TypeError):
            return False, None
    
    @staticmethod
    def validar_km_viagem(km_inicial: int, km_final: int) -> bool:
        """Valida se KM final é maior ou igual ao inicial."""
        return km_final >= km_inicial


class Sanitizador:
    """Classe para sanitização de dados de entrada."""
    
    @staticmethod
    def sanitizar_texto(texto: str) -> str:
        """Remove espaços extras e converte para title case."""
        return ' '.join(texto.strip().split()).title()
    
    @staticmethod
    def sanitizar_destino(destino: str) -> str:
        """Sanitização específica para campo de destino."""
        destino_limpo = ' '.join(destino.strip().split())
        return destino_limpo.upper() if destino_limpo.isupper() else destino_limpo.title()