"""
Módulo que define o modelo Viagem.
"""

from datetime import datetime
from typing import Dict, Optional
from utils.data_utils import DataUtils

class Viagem:
    """Classe que representa uma viagem no diário de bordo."""
    
    def __init__(self, data: str, horario_saida: datetime, km_inicial: int, destino: str):
        """
        Inicializa uma nova viagem.
        
        Args:
            data: Data no formato DD/MM/YYYY
            horario_saida: Objeto datetime com horário de saída
            km_inicial: Quilometragem inicial
            destino: Destino da viagem
        """
        self.data = data
        self.horario_saida = horario_saida
        self.km_inicial = km_inicial
        self.destino = destino
        self.horario_chegada: Optional[datetime] = None
        self.km_final: Optional[int] = None
    
    def finalizar_viagem(self, horario_chegada: datetime, km_final: int):
        """Registra o término da viagem."""
        self.horario_chegada = horario_chegada
        self.km_final = km_final
    
    def calcular_duracao(self) -> str:
        """Calcula a duração da viagem."""
        if not self.horario_chegada:
            return "N/A"
        return DataUtils.calcular_duracao(self.horario_saida, self.horario_chegada)
    
    def calcular_km_percorrido(self) -> int:
        """Calcula a distância percorrida."""
        if self.km_final is None:
            return 0
        return self.km_final - self.km_inicial
    
    def to_dict(self, id_viagem: int) -> Dict:
        """Converte a viagem para um dicionário serializável."""
        return {
            'ID': id_viagem,
            'data': self.data,
            'hora_inicial': DataUtils.formatar_hora(self.horario_saida),
            'km_inicial': self.km_inicial,
            'hora_final': DataUtils.formatar_hora(self.horario_chegada) if self.horario_chegada else "N/A",
            'km_final': self.km_final if self.km_final is not None else "N/A",
            'destino': self.destino,
            'total_km': self.calcular_km_percorrido(),
            'tempo_levado': self.calcular_duracao(),
        }
    
    def __repr__(self) -> str:
        return f"Viagem({self.data}, {self.destino}, {self.calcular_km_percorrido()}km)"