"""
Módulo de view para a interface do diário de bordo.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from controllers.viagem_controller import ViagemController
from utils.data_utils import DataUtils

class ViagemView:
    """Classe que implementa a interface do usuário usando Streamlit."""

    def __init__(self):
        self.controller = ViagemController()
        self._configurar_pagina()

    def _configurar_pagina(self):
        """Configurações iniciais da página."""
        st.set_page_config(
            page_title="Diário de Bordo",
            page_icon="🚗",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        st.title("📖 Diário de Bordo")

    def _mostrar_cabecalho(self):
        """Exibe informações no cabeçalho."""
        st.markdown("""
            **Registro completo de viagens**
            *Inicie novas viagens, finalize as em andamento e consulte o histórico*
        """)

    def _mostrar_menu_lateral(self):
        """Exibe e gerencia o menu lateral."""
        with st.sidebar:
            st.header("Menu")
            return st.selectbox(
                "Selecione uma opção",
                ["Iniciar Viagem", "Finalizar Viagem", "Exibir Histórico", "Exportar Histórico"],
                key="menu_principal"
            )

    def _mostrar_formulario_inicio_viagem(self):
        """Exibe o formulário para iniciar uma nova viagem."""
        st.subheader("Iniciar Nova Viagem")

        with st.form(key="form_iniciar_viagem", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                data = st.date_input(
                    "Data da Viagem",
                    datetime.now(),
                    format="DD/MM/YYYY"
                ).strftime(DataUtils.FORMATO_DATA)

                horario_saida = st.text_input(
                    "Horário de Saída (HH:MM)",
                    value=DataUtils.hora_atual_formatada(),
                    help="Formato 24 horas"
                )

            with col2:
                km_inicial = st.number_input(
                    "Quilometragem Inicial",
                    min_value=0,
                    step=1,
                    value=0
                )

                destino = st.text_input(
                    "Destino",
                    placeholder="Digite o destino da viagem",
                    max_chars=100
                )

            if st.form_submit_button("Iniciar Viagem", use_container_width=True):
                resultado = self.controller.iniciar_viagem(data, horario_saida, km_inicial, destino)

                if resultado['success']:
                    st.success(resultado['message'])
                    st.balloons()
                else:
                    st.error(resultado['message'])

    def _mostrar_formulario_fim_viagem(self):
        """Exibe o formulário para finalizar a viagem ativa."""
        st.subheader("Finalizar Viagem Ativa")

        if not self.controller.verificar_viagem_ativa():
            st.info("ℹ️ Não há viagem ativa para finalizar.")
            return

        with st.form(key="form_finalizar_viagem", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                data = st.date_input(
                    "Data de Chegada",
                    datetime.now(),
                    format="DD/MM/YYYY"
                ).strftime(DataUtils.FORMATO_DATA)

                horario_chegada = st.text_input(
                    "Horário de Chegada (HH:MM)",
                    value=DataUtils.hora_atual_formatada(),
                    help="Formato 24 horas"
                )

            with col2:
                km_final = st.number_input(
                    "Quilometragem Final",
                    min_value=0,
                    step=1,
                    value=0
                )

            if st.form_submit_button("Finalizar Viagem", use_container_width=True):
                resultado = self.controller.finalizar_viagem(data, horario_chegada, km_final)

                if resultado['success']:
                    st.success(resultado['message'])
                    st.balloons()
                else:
                    st.error(resultado['message'])

    def _mostrar_historico(self):

        """Exibe e permite edição do histórico de viagens."""
        try:
            historico = self.controller.obter_historico()

            # Verificar se o histórico está vazio
            if historico.empty if hasattr(historico, 'empty') else not historico:
                st.info("Nenhuma viagem registrada ainda.")
                return

            # Converter para DataFrame se não for
            if not isinstance(historico, pd.DataFrame):
                df = pd.DataFrame(historico)
            else:
                df = historico.copy()

            # Converter coluna de data para datetime
            df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')

            # Configuração das colunas
            column_config = {
                "data": st.column_config.DateColumn(
                    "Data",
                    format="DD/MM/YYYY",
                    help="Data da viagem"
                ),
                "hora_inicial": st.column_config.TextColumn(
                    "Hora Saída",
                    help="Formato HH:MM"
                ),
                "km_inicial": st.column_config.NumberColumn(
                    "KM Inicial",
                    format="%d",
                    step=1
                ),
                "hora_final": st.column_config.TextColumn(
                    "Hora Chegada",
                    help="Formato HH:MM"
                ),
                "km_final": st.column_config.NumberColumn(
                    "KM Final",
                    format="%d",
                    step=1
                ),
                "destino": st.column_config.TextColumn(
                    "Destino"
                ),
                "total_km": st.column_config.NumberColumn(
                    "KM Percorridos",
                    disabled=True
                ),
                "tempo_levado": st.column_config.TextColumn(
                    "Duração",
                    disabled=True
                )
            }

            # Exibir editor de dados
            edited_df = st.data_editor(
                df,
                column_config=column_config,
                use_container_width=True,
                num_rows="dynamic",
                key="editor_historico"
            )

            if st.button("Salvar Alterações"):
                # Converter data de volta para string no formato original
                edited_df['data'] = edited_df['data'].dt.strftime('%d/%m/%Y')

                # Enviar dados atualizados para o controller
                resultado = self.controller.atualizar_historico(edited_df)

                if resultado['success']:
                    st.success("Histórico atualizado com sucesso!")
                    st.rerun()
                else:
                    st.error(f"Erro ao salvar: {resultado['message']}")

        except Exception as e:
            st.error(f"Erro ao processar histórico: {str(e)}")

    def _mostrar_exportacao(self):
        """Exibe a interface para exportar o histórico."""
        st.subheader("Exportar Histórico")

        caminho = st.text_input(
            "Caminho do arquivo Excel",
            value="historico_viagens.xlsx",
            help="Caminho onde o arquivo será salvo"
        )

        if st.button("Exportar para Excel", use_container_width=True):
            with st.spinner("Exportando dados..."):
                resultado = self.controller.exportar_historico(caminho)

            if resultado['success']:
                st.success(resultado['message'])
                st.download_button(
                    label="Baixar Arquivo",
                    data=open(caminho, "rb").read(),
                    file_name=caminho,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            else:
                st.error(resultado['message'])

    def executar(self):
        """Método principal para execução da interface."""
        self._mostrar_cabecalho()
        opcao_selecionada = self._mostrar_menu_lateral()

        if opcao_selecionada == "Iniciar Viagem":
            self._mostrar_formulario_inicio_viagem()
        elif opcao_selecionada == "Finalizar Viagem":
            self._mostrar_formulario_fim_viagem()
        elif opcao_selecionada == "Exibir Histórico":
            self._mostrar_historico()
        elif opcao_selecionada == "Exportar Histórico":
            self._mostrar_exportacao()