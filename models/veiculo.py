"""
Módulo que define o modelo Veiculo para gerenciamento de viagens.
"""

import json
import os
from typing import List, Dict, Optional
import pandas as pd
from pathlib import Path
from utils.data_utils import DataUtils, Validador, Sanitizador
from models.viagem import Viagem

class Veiculo:
    """Classe que representa um veículo e gerencia suas viagens."""
    
    def __init__(self, arquivo_dados: str = 'data/historico_viagens.json'):
        """Inicializa o veículo e carrega os dados do arquivo."""
        self.viagens: List[Viagem] = []
        self.arquivo_dados = arquivo_dados
        self._inicializar_diretorio_dados()
        self.carregar_dados()
    
    def _inicializar_diretorio_dados(self):
        """Garante que o diretório de dados existe."""
        Path(os.path.dirname(self.arquivo_dados)).mkdir(parents=True, exist_ok=True)
    
    def iniciar_viagem(self, data: str, horario_saida: str, km_inicial: int, destino: str) -> Dict:
        """
        Inicia uma nova viagem.
        
        Returns:
            Dict: {'success': bool, 'message': str}
        """
        # Validação e sanitização
        destino = Sanitizador.sanitizar_destino(destino)
        valido_km, km = Validador.validar_km(km_inicial)
        
        if not valido_km:
            return {'success': False, 'message': 'Quilometragem inicial inválida'}
        
        valido, horario_saida_dt = DataUtils.validar_data_hora(data, horario_saida)
        if not valido:
            return {'success': False, 'message': 'Data ou horário de saída inválidos'}
        
        # Cria e armazena a nova viagem
        nova_viagem = Viagem(data, horario_saida_dt, km, destino)
        self.viagens.append(nova_viagem)
        self.salvar_dados()
        
        return {'success': True, 'message': 'Viagem iniciada com sucesso!'}
    
    def finalizar_viagem(self, data: str, horario_chegada: str, km_final: int) -> Dict:
        """
        Finaliza a viagem ativa.
        
        Returns:
            Dict: {'success': bool, 'message': str}
        """
        if not self.viagens:
            return {'success': False, 'message': 'Não há viagens registradas'}
        
        if self.viagens[-1].horario_chegada:
            return {'success': False, 'message': 'A última viagem já foi finalizada'}
        
        # Validação e sanitização
        valido_km, km = Validador.validar_km(km_final)
        if not valido_km:
            return {'success': False, 'message': 'Quilometragem final inválida'}
        
        if not Validador.validar_km_viagem(self.viagens[-1].km_inicial, km):
            return {'success': False, 'message': 'KM final menor que KM inicial'}
        
        valido, horario_chegada_dt = DataUtils.validar_data_hora(data, horario_chegada)
        if not valido:
            return {'success': False, 'message': 'Data ou horário de chegada inválidos'}
        
        # Finaliza a viagem
        self.viagens[-1].finalizar_viagem(horario_chegada_dt, km)
        self.salvar_dados()
        
        return {'success': True, 'message': 'Viagem finalizada com sucesso!'}
    
    def obter_historico_viagens(self) -> List[Dict]:
        """Retorna o histórico de viagens como lista de dicionários."""
        return [viagem.to_dict(idx + 1) for idx, viagem in enumerate(self.viagens)]
    
    def salvar_dados(self):
        """Salva as viagens no arquivo JSON."""
        try:
            with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
                json.dump(self.obter_historico_viagens(), f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Erro ao salvar dados: {e}")
    
    def carregar_dados(self):
        """Carrega as viagens do arquivo JSON."""
        if not os.path.exists(self.arquivo_dados):
            return
            
        try:
            with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            self.viagens.clear()
            for viagem_data in dados:
                try:
                    valido, horario_saida = DataUtils.validar_data_hora(
                        viagem_data['data'], 
                        viagem_data['hora_inicial']
                    )
                    if not valido:
                        continue
                        
                    nova_viagem = Viagem(
                        viagem_data['data'],
                        horario_saida,
                        viagem_data['km_inicial'],
                        viagem_data['destino']
                    )
                    
                    if viagem_data['hora_final'] != "N/A":
                        valido, horario_chegada = DataUtils.validar_data_hora(
                            viagem_data['data'], 
                            viagem_data['hora_final']
                        )
                        if valido:
                            nova_viagem.finalizar_viagem(
                                horario_chegada,
                                viagem_data['km_final']
                            )
                    
                    self.viagens.append(nova_viagem)
                except (KeyError, ValueError) as e:
                    print(f"Erro ao carregar viagem: {e}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Erro ao carregar arquivo: {e}")
    
    def exportar_para_excel(self, caminho: str) -> Dict:
        """
        Exporta o histórico para Excel.
        
        Returns:
            Dict: {'success': bool, 'message': str}
        """
        try:
            df = pd.DataFrame(self.obter_historico_viagens())
            df.to_excel(caminho, index=False, engine='openpyxl')
            return {'success': True, 'message': f'Dados exportados para {caminho}'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao exportar: {str(e)}'}
    
    def viagem_ativa(self) -> bool:
        """Verifica se há uma viagem ativa (iniciada mas não finalizada)."""
        return bool(self.viagens) and self.viagens[-1].horario_chegada is None