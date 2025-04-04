import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from database.database import DatabaseManager


class ViagemController:
    """Controlador para gerenciar operações relacionadas a viagens."""

    def __init__(self):
        self.db = DatabaseManager()
        self.FORMATO_DATA = '%d/%m/%Y'
        self.FORMATO_HORA = '%H:%M'

    def _get_data_atual(self) -> str:
        """Retorna a data atual formatada."""
        return datetime.now().strftime(self.FORMATO_DATA)

    def _get_hora_atual(self) -> str:
        """Retorna a hora atual formatada."""
        return datetime.now().strftime(self.FORMATO_HORA)

    def obter_ultimo_km(self) -> Optional[int]:
        """Obtém o último KM final registrado no histórico."""
        try:
            historico = self.db.obter_viagens()
            if historico:
                ultima_viagem = historico[0]  # Ordenado por data DESC
                return ultima_viagem.get('km_final')
            return None
        except Exception as e:
            print(f"Erro ao obter último KM: {str(e)}")
            return None

    def iniciar_viagem(self, km_inicial: int, destino: str,
                       data: str = None, hora_saida: str = None) -> Dict[str, any]:
        """
        Inicia uma nova viagem.

        Args:
            km_inicial: Quilometragem inicial (obrigatório)
            destino: Destino da viagem (obrigatório)
            data: Data da viagem (opcional, usa atual se None)
            hora_saida: Hora de saída (opcional, usa atual se None)

        Returns:
            Dicionário com status e mensagem da operação
        """
        data = data or self._get_data_atual()
        hora_saida = hora_saida or self._get_hora_atual()

        try:
            viagem_id = self.db.iniciar_viagem(data, hora_saida, km_inicial, destino)
            return {
                'success': True,
                'message': 'Viagem iniciada com sucesso!',
                'viagem_id': viagem_id
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao iniciar viagem: {str(e)}'
            }

    def finalizar_viagem(self, viagem_id: int, km_final: int,
                         hora_chegada: str = None) -> Dict[str, any]:
        """
        Finaliza uma viagem existente.

        Args:
            viagem_id: ID da viagem (obrigatório)
            km_final: Quilometragem final (obrigatório)
            hora_chegada: Hora de chegada (opcional, usa atual se None)

        Returns:
            Dicionário com status e mensagem da operação
        """
        hora_chegada = hora_chegada or self._get_hora_atual()

        try:
            success = self.db.finalizar_viagem(viagem_id, hora_chegada, km_final)
            if success:
                return {
                    'success': True,
                    'message': 'Viagem finalizada com sucesso!'
                }
            return {
                'success': False,
                'message': 'Viagem não encontrada ou já finalizada'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao finalizar viagem: {str(e)}'
            }

    def obter_historico(self) -> List[Dict]:
        """
        Retorna o histórico completo de viagens.

        Returns:
            Lista de dicionários com informações das viagens
        """
        try:
            return self.db.obter_viagens()
        except Exception as e:
            print(f"Erro ao obter histórico: {str(e)}")
            return []

    def obter_viagem_ativa(self) -> Optional[Dict]:
        """
        Retorna a viagem ativa (não finalizada), se existir.

        Returns:
            Dicionário com informações da viagem ou None
        """
        try:
            return self.db.obter_viagem_ativa()
        except Exception as e:
            print(f"Erro ao obter viagem ativa: {str(e)}")
            return None

    def atualizar_viagem(self, viagem_id: int, **kwargs) -> Dict[str, any]:
        """
        Atualiza informações de uma viagem.

        Args:
            viagem_id: ID da viagem
            kwargs: Campos a serem atualizados

        Returns:
            Dicionário com status e mensagem da operação
        """
        try:
            success = self.db.atualizar_viagem(viagem_id, **kwargs)
            return {
                'success': success,
                'message': 'Viagem atualizada com sucesso!' if success else 'Falha ao atualizar viagem'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao atualizar viagem: {str(e)}'
            }

    def exportar_historico(self, formato: str, caminho: str = None) -> Dict[str, any]:
        """
        Exporta o histórico de viagens para o formato especificado.

        Args:
            formato: 'excel', 'json' ou 'csv'
            caminho: Caminho do arquivo de destino (opcional)

        Returns:
            Dicionário com status e mensagem da operação
        """
        try:
            historico = self.obter_historico()
            if not historico:
                return {'success': False, 'message': 'Nenhum dado para exportar'}

            df = pd.DataFrame(historico)

            # Definir caminho padrão se não fornecido
            if not caminho:
                data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
                caminho = f"historico_viagens_{data_hora}.{formato.lower()}"

            # Configurações de codificação para Português-Brasil
            encoding = 'utf-8-sig'  # UTF-8 com BOM para Excel e CSV

            # Realizar a exportação conforme o formato
            formato = formato.lower()
            if formato == 'excel':
                if not caminho.endswith('.xlsx'):
                    caminho = os.path.splitext(caminho)[0] + '.xlsx'
                df.to_excel(caminho, index=False, engine='openpyxl')
                return {'success': True, 'message': f'Dados exportados para Excel: {caminho}', 'path': caminho}

            elif formato == 'json':
                df.to_json(caminho, orient='records', indent=4, force_ascii=False)
                return {'success': True, 'message': f'Dados exportados para JSON: {caminho}', 'path': caminho}

            elif formato == 'csv':
                df.to_csv(caminho, index=False, encoding=encoding, sep=';', decimal=',')
                return {'success': True, 'message': f'Dados exportados para CSV: {caminho}', 'path': caminho}

            else:
                return {'success': False, 'message': 'Formato de exportação inválido'}

        except Exception as e:
            return {'success': False, 'message': f'Erro ao exportar dados: {str(e)}'}


# from datetime import datetime
# from typing import Dict, List, Optional
# from models.viagem import Viagem
# from database import DatabaseManager
#
# class ViagemController:
#     """Controlador para gerenciar operações relacionadas a viagens."""
#
#     def __init__(self):
#         self.db = DatabaseManager()
#         self.FORMATO_DATA = '%d/%m/%Y'
#         self.FORMATO_HORA = '%H:%M'
#
#     def _get_data_atual(self) -> str:
#         """Retorna a data atual formatada."""
#         return datetime.now().strftime(self.FORMATO_DATA)
#
#     def _get_hora_atual(self) -> str:
#         """Retorna a hora atual formatada."""
#         return datetime.now().strftime(self.FORMATO_HORA)
#
#     def iniciar_viagem(self, km_inicial: int, destino: str,
#                        data: str = None, hora_saida: str = None) -> Dict[str, any]:
#         """
#         Inicia uma nova viagem.
#
#         Args:
#             data: Data da viagem (opcional, usa atual se None)
#             hora_saida: Hora de saída (opcional, usa atual se None)
#             km_inicial: Quilometragem inicial
#             destino: Destino da viagem
#
#         Returns:
#             Dicionário com status e mensagem da operação
#         """
#         data = data or self._get_data_atual()
#         hora_saida = hora_saida or self._get_hora_atual()
#
#         try:
#             viagem_id = self.db.iniciar_viagem(data, hora_saida, km_inicial, destino)
#             return {
#                 'success': True,
#                 'message': 'Viagem iniciada com sucesso!',
#                 'viagem_id': viagem_id
#             }
#         except Exception as e:
#             return {
#                 'success': False,
#                 'message': f'Erro ao iniciar viagem: {str(e)}'
#             }
#
#     def finalizar_viagem(self, viagem_id: int,km_final: int, hora_chegada: str = None) -> Dict[str, any]:
#         """
#         Finaliza uma viagem existente.
#
#         Args:
#             viagem_id: ID da viagem
#             hora_chegada: Hora de chegada (opcional, usa atual se None)
#             km_final: Quilometragem final
#
#         Returns:
#             Dicionário com status e mensagem da operação
#         """
#         hora_chegada = hora_chegada or self._get_hora_atual()
#
#         try:
#             success = self.db.finalizar_viagem(viagem_id, hora_chegada, km_final)
#             if success:
#                 return {
#                     'success': True,
#                     'message': 'Viagem finalizada com sucesso!'
#                 }
#             return {
#                 'success': False,
#                 'message': 'Viagem não encontrada ou já finalizada'
#             }
#         except Exception as e:
#             return {
#                 'success': False,
#                 'message': f'Erro ao finalizar viagem: {str(e)}'
#             }
#
#     def obter_historico(self) -> List[Dict]:
#         """
#         Retorna o histórico completo de viagens.
#
#         Returns:
#             Lista de dicionários com informações das viagens
#         """
#         try:
#             return self.db.obter_viagens()
#         except Exception as e:
#             print(f"Erro ao obter histórico: {str(e)}")
#             return []
#
#     def obter_viagem_ativa(self) -> Optional[Dict]:
#         """
#         Retorna a viagem ativa (não finalizada), se existir.
#
#         Returns:
#             Dicionário com informações da viagem ou None
#         """
#         try:
#             return self.db.obter_viagem_ativa()
#         except Exception as e:
#             print(f"Erro ao obter viagem ativa: {str(e)}")
#             return None
#
#     def atualizar_viagem(self, viagem_id: int, **kwargs) -> Dict[str, any]:
#         """
#         Atualiza informações de uma viagem.
#
#         Args:
#             viagem_id: ID da viagem
#             kwargs: Campos a serem atualizados
#
#         Returns:
#             Dicionário com status e mensagem da operação
#         """
#         try:
#             success = self.db.atualizar_viagem(viagem_id, **kwargs)
#             return {
#                 'success': success,
#                 'message': 'Viagem atualizada com sucesso!' if success else 'Falha ao atualizar viagem'
#             }
#         except Exception as e:
#             return {
#                 'success': False,
#                 'message': f'Erro ao atualizar viagem: {str(e)}'
#             }
#
# # """
# # Módulo do controlador para gerenciamento de viagens.
# # """
# #
# # from typing import Dict, Any
# # import pandas as pd
# # from models.veiculo import Veiculo
# # from models.viagem import Viagem
# # from utils.data_utils import DataUtils
# #
# # class ViagemController:
# #     """Controlador para operações relacionadas a viagens."""
# #
# #     def __init__(self):
# #         self.veiculo = Veiculo()
# #
# #     def iniciar_viagem(self, data: str, horario_saida: str, km_inicial: int, destino: str) -> Dict[str, Any]:
# #         """
# #         Inicia uma nova viagem.
# #
# #         Args:
# #             data: Data no formato DD/MM/YYYY (opcional, usa hoje se vazio)
# #             horario_saida: Horário no formato HH:MM (opcional, usa agora se vazio)
# #             km_inicial: Quilometragem inicial
# #             destino: Destino da viagem
# #
# #         Returns:
# #             Dict: {'success': bool, 'message': str}
# #         """
# #         # Valores padrão se não fornecidos
# #         data = data or DataUtils.hoje_formatado()
# #         horario_saida = horario_saida or DataUtils.hora_atual_formatada()
# #
# #         return self.veiculo.iniciar_viagem(data, horario_saida, km_inicial, destino)
# #
# #     def finalizar_viagem(self, data: str, horario_chegada: str, km_final: int) -> Dict[str, Any]:
# #         """
# #         Finaliza a viagem ativa.
# #
# #         Args:
# #             data: Data no formato DD/MM/YYYY (opcional, usa hoje se vazio)
# #             horario_chegada: Horário no formato HH:MM (opcional, usa agora se vazio)
# #             km_final: Quilometragem final
# #
# #         Returns:
# #             Dict: {'success': bool, 'message': str}
# #         """
# #         # Valores padrão se não fornecidos
# #         data = data or DataUtils.hoje_formatado()
# #         horario_chegada = horario_chegada or DataUtils.hora_atual_formatada()
# #
# #         return self.veiculo.finalizar_viagem(data, horario_chegada, km_final)
# #
# #     def obter_historico(self) -> pd.DataFrame:
# #         """
# #         Obtém o histórico de viagens como DataFrame.
# #
# #         Returns:
# #             pd.DataFrame: DataFrame com o histórico
# #         """
# #         historico = self.veiculo.obter_historico_viagens()
# #         return pd.DataFrame(historico).set_index("ID") if historico else pd.DataFrame()
# #
# #     def atualizar_historico(self, df: pd.DataFrame) -> Dict[str, Any]:
# #         """
# #         Atualiza o histórico com base em um DataFrame editado.
# #
# #         Args:
# #             df: DataFrame com dados editados
# #
# #         Returns:
# #             Dict: {'success': bool, 'message': str}
# #         """
# #         try:
# #             # Converte o DataFrame para lista de dicionários
# #             dados = df.reset_index().to_dict('records')
# #
# #             # Limpa as viagens atuais
# #             self.veiculo.viagens.clear()
# #
# #             # Recria as viagens a partir dos dados editados
# #             for viagem_data in dados:
# #                 try:
# #                     valido, horario_saida = DataUtils.validar_data_hora(
# #                         viagem_data['data'],
# #                         viagem_data['hora_inicial']
# #                     )
# #                     if not valido:
# #                         continue
# #
# #                     nova_viagem = Viagem(
# #                         viagem_data['data'],
# #                         horario_saida,
# #                         viagem_data['km_inicial'],
# #                         viagem_data['destino']
# #                     )
# #
# #                     if viagem_data['hora_final'] != "N/A":
# #                         valido, horario_chegada = DataUtils.validar_data_hora(
# #                             viagem_data['data'],
# #                             viagem_data['hora_final']
# #                         )
# #                         if valido:
# #                             nova_viagem.finalizar_viagem(
# #                                 horario_chegada,
# #                                 viagem_data['km_final']
# #                             )
# #
# #                     self.veiculo.viagens.append(nova_viagem)
# #                 except (KeyError, ValueError) as e:
# #                     print(f"Erro ao processar viagem: {e}")
# #
# #             self.veiculo.salvar_dados()
# #             return {'success': True, 'message': 'Histórico atualizado com sucesso!'}
# #         except Exception as e:
# #             return {'success': False, 'message': f'Erro ao atualizar histórico: {str(e)}'}
# #
# #     def exportar_historico(self, caminho: str) -> Dict[str, Any]:
# #         """
# #         Exporta o histórico para um arquivo Excel.
# #
# #         Args:
# #             caminho: Caminho do arquivo de destino
# #
# #         Returns:
# #             Dict: {'success': bool, 'message': str}
# #         """
# #         return self.veiculo.exportar_para_excel(caminho)
# #
# #     def verificar_viagem_ativa(self) -> bool:
# #         """
# #         Verifica se há uma viagem ativa.
# #
# #         Returns:
# #             bool: True se há viagem ativa, False caso contrário
# #         """
# #         return self.veiculo.viagem_ativa()