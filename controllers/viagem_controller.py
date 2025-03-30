"""
Módulo do controlador para gerenciamento de viagens.
"""

from typing import Dict, Any
import pandas as pd
from models.veiculo import Veiculo
from models.viagem import Viagem
from utils.data_utils import DataUtils

class ViagemController:
    """Controlador para operações relacionadas a viagens."""
    
    def __init__(self):
        self.veiculo = Veiculo()
    
    def iniciar_viagem(self, data: str, horario_saida: str, km_inicial: int, destino: str) -> Dict[str, Any]:
        """
        Inicia uma nova viagem.
        
        Args:
            data: Data no formato DD/MM/YYYY (opcional, usa hoje se vazio)
            horario_saida: Horário no formato HH:MM (opcional, usa agora se vazio)
            km_inicial: Quilometragem inicial
            destino: Destino da viagem
            
        Returns:
            Dict: {'success': bool, 'message': str}
        """
        # Valores padrão se não fornecidos
        data = data or DataUtils.hoje_formatado()
        horario_saida = horario_saida or DataUtils.hora_atual_formatada()
        
        return self.veiculo.iniciar_viagem(data, horario_saida, km_inicial, destino)
    
    def finalizar_viagem(self, data: str, horario_chegada: str, km_final: int) -> Dict[str, Any]:
        """
        Finaliza a viagem ativa.
        
        Args:
            data: Data no formato DD/MM/YYYY (opcional, usa hoje se vazio)
            horario_chegada: Horário no formato HH:MM (opcional, usa agora se vazio)
            km_final: Quilometragem final
            
        Returns:
            Dict: {'success': bool, 'message': str}
        """
        # Valores padrão se não fornecidos
        data = data or DataUtils.hoje_formatado()
        horario_chegada = horario_chegada or DataUtils.hora_atual_formatada()
        
        return self.veiculo.finalizar_viagem(data, horario_chegada, km_final)
    
    def obter_historico(self) -> pd.DataFrame:
        """
        Obtém o histórico de viagens como DataFrame.
        
        Returns:
            pd.DataFrame: DataFrame com o histórico
        """
        historico = self.veiculo.obter_historico_viagens()
        return pd.DataFrame(historico).set_index("ID") if historico else pd.DataFrame()
    
    def atualizar_historico(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Atualiza o histórico com base em um DataFrame editado.
        
        Args:
            df: DataFrame com dados editados
            
        Returns:
            Dict: {'success': bool, 'message': str}
        """
        try:
            # Converte o DataFrame para lista de dicionários
            dados = df.reset_index().to_dict('records')
            
            # Limpa as viagens atuais
            self.veiculo.viagens.clear()
            
            # Recria as viagens a partir dos dados editados
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
                    
                    self.veiculo.viagens.append(nova_viagem)
                except (KeyError, ValueError) as e:
                    print(f"Erro ao processar viagem: {e}")
            
            self.veiculo.salvar_dados()
            return {'success': True, 'message': 'Histórico atualizado com sucesso!'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao atualizar histórico: {str(e)}'}
    
    def exportar_historico(self, caminho: str) -> Dict[str, Any]:
        """
        Exporta o histórico para um arquivo Excel.
        
        Args:
            caminho: Caminho do arquivo de destino
            
        Returns:
            Dict: {'success': bool, 'message': str}
        """
        return self.veiculo.exportar_para_excel(caminho)
    
    def verificar_viagem_ativa(self) -> bool:
        """
        Verifica se há uma viagem ativa.
        
        Returns:
            bool: True se há viagem ativa, False caso contrário
        """
        return self.veiculo.viagem_ativa()