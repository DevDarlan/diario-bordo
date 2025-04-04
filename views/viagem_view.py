import os
import streamlit as st
import pandas as pd
from datetime import datetime
from controllers.viagem_controller import ViagemController


class ViagemView:
    """Classe responsável pela interface do usuário do Diário de Bordo."""

    def __init__(self):
        self.controller = ViagemController()
        self._configurar_pagina()

    def _configurar_pagina(self):
        """Configurações iniciais da página."""
        st.set_page_config(
            page_title="Diário de Bordo",
            page_icon="🚗",
            layout="wide"
        )
        st.title("📖 Diário de Bordo - Gestão de Viagens")

    def executar(self):
        """Método principal para execução da aplicação."""
        self.mostrar_menu_principal()

    def mostrar_menu_principal(self):
        """Exibe o menu principal e gerencia a navegação."""
        opcao = st.sidebar.selectbox(
            "Menu",
            ["Iniciar Viagem", "Finalizar Viagem", "Histórico", "Editar Viagem", "Exportar Dados"]
        )

        if opcao == "Iniciar Viagem":
            self._mostrar_formulario_inicio()
        elif opcao == "Finalizar Viagem":
            self._mostrar_formulario_fim()
        elif opcao == "Histórico":
            self._mostrar_historico()
        elif opcao == "Editar Viagem":
            self._mostrar_edicao()
        else:
            self._mostrar_exportacao()

    def _mostrar_formulario_inicio(self):
        """Formulário para iniciar nova viagem."""
        st.header("Iniciar Nova Viagem")

        # Obter último KM final como valor padrão
        ultimo_km = self.controller.obter_ultimo_km()
        km_inicial_padrao = ultimo_km if ultimo_km is not None else 0

        with st.form("form_inicio_viagem", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                data = st.date_input("Data da Viagem", datetime.now())
                hora_saida = st.time_input("Hora de Saída", datetime.now())

            with col2:
                km_inicial = st.number_input(
                    "KM Inicial",
                    min_value=0,
                    value=km_inicial_padrao,
                    step=1,
                    help=f"Último KM final registrado: {ultimo_km if ultimo_km is not None else 'N/A'}"
                )
                destino = st.text_input("Destino", max_chars=100)

            usar_hora_atual = st.checkbox("Usar hora atual", value=True)

            if st.form_submit_button("Registrar Viagem"):
                data_str = data.strftime("%d/%m/%Y")
                hora_str = hora_saida.strftime("%H:%M") if not usar_hora_atual else None

                resultado = self.controller.iniciar_viagem(
                    km_inicial=km_inicial,
                    destino=destino.strip(),
                    data=data_str,
                    hora_saida=hora_str
                )

                if resultado['success']:
                    st.success(resultado['message'])
                    st.balloons()
                else:
                    st.error(resultado['message'])

    def _mostrar_formulario_fim(self):
        """Formulário para finalizar viagem."""
        st.header("Finalizar Viagem Ativa")

        viagem_ativa = self.controller.obter_viagem_ativa()

        if not viagem_ativa:
            st.info("Não há viagens ativas para finalizar.")
            return

        st.write(
            f"Viagem para {viagem_ativa['destino']} iniciada em {viagem_ativa['data']} às {viagem_ativa['hora_saida']}")

        with st.form("form_fim_viagem"):
            col1, col2 = st.columns(2)

            with col1:
                data = st.date_input("Data de Chegada", datetime.now())
                hora_chegada = st.time_input("Hora de Chegada", datetime.now())

            with col2:
                km_final = st.number_input(
                    "KM Final",
                    min_value=viagem_ativa['km_inicial'],
                    value=viagem_ativa['km_inicial'] + 100,
                    step=1
                )

            usar_hora_atual = st.checkbox("Usar hora atual", value=True)

            if st.form_submit_button("Finalizar Viagem"):
                data_str = data.strftime("%d/%m/%Y")
                hora_str = hora_chegada.strftime("%H:%M") if not usar_hora_atual else None

                resultado = self.controller.finalizar_viagem(
                    viagem_id=viagem_ativa['id'],
                    hora_chegada=hora_str,
                    km_final=km_final
                )

                if resultado['success']:
                    st.success(resultado['message'])
                    st.rerun()
                else:
                    st.error(resultado['message'])

    def _mostrar_historico(self):
        """Exibe o histórico de viagens."""
        st.header("Histórico de Viagens")

        historico = self.controller.obter_historico()

        if not historico:
            st.info("Nenhuma viagem registrada ainda.")
            return

        df = pd.DataFrame(historico)

        # Calcula duração e km percorrido para exibição
        df['duracao'] = df.apply(lambda x: self._calcular_duracao(x['hora_saida'], x['hora_chegada']), axis=1)
        df['km_percorrido'] = df.apply(lambda x: x['km_final'] - x['km_inicial'] if x['km_final'] else 0, axis=1)

        st.dataframe(
            df[['id', 'data', 'hora_saida', 'hora_chegada', 'destino', 'km_inicial', 'km_final', 'km_percorrido',
                'duracao']],
            use_container_width=True,
            hide_index=True
        )

    def _mostrar_edicao(self):
        """Interface para edição de viagens."""
        st.header("Editar Viagem")

        historico = self.controller.obter_historico()

        if not historico:
            st.info("Nenhuma viagem registrada para edição.")
            return

        viagem_id = st.selectbox(
            "Selecione a viagem para editar",
            options=[(v['id'], f"{v['data']} - {v['destino']}") for v in historico],
            format_func=lambda x: x[1]
        )[0]

        viagem = next((v for v in historico if v['id'] == viagem_id), None)

        if not viagem:
            st.error("Viagem não encontrada!")
            return

        with st.form("form_edicao_viagem"):
            col1, col2 = st.columns(2)

            with col1:
                nova_data = st.text_input("Data", value=viagem['data'])
                nova_hora_saida = st.text_input("Hora Saída", value=viagem['hora_saida'])

            with col2:
                novo_km_inicial = st.number_input(
                    "KM Inicial",
                    value=viagem['km_inicial'],
                    min_value=0,
                    step=1
                )
                novo_destino = st.text_input("Destino", value=viagem['destino'])

            if viagem['hora_chegada']:
                st.warning("Viagem já finalizada - não é possível alterar dados de chegada")
            else:
                st.info("Viagem ainda não finalizada")

            if st.form_submit_button("Salvar Alterações"):
                atualizacoes = {
                    'data': nova_data,
                    'hora_saida': nova_hora_saida,
                    'km_inicial': novo_km_inicial,
                    'destino': novo_destino
                }

                resultado = self.controller.atualizar_viagem(viagem_id, **atualizacoes)

                if resultado['success']:
                    st.success(resultado['message'])
                    st.rerun()
                else:
                    st.error(resultado['message'])

    def _mostrar_exportacao(self):
        """Interface para exportação do histórico."""
        st.header("Exportar Histórico")

        historico = self.controller.obter_historico()

        if not historico:
            st.warning("Nenhum dado disponível para exportação")
            return

        # Seleção do formato
        formato = st.radio(
            "Selecione o formato de exportação",
            ["Excel", "JSON", "CSV"],
            horizontal=True
        )

        # Configurações específicas para Português-Brasil
        with st.expander("Configurações de Exportação"):
            if formato == "CSV":
                separador = st.selectbox("Separador", [";", ","], index=0)
                decimal = st.selectbox("Separador decimal", [",", "."], index=0)
            elif formato == "Excel":
                st.info("Excel: Formato otimizado para Português-Brasil")

        # Nome do arquivo personalizado
        nome_arquivo = st.text_input(
            "Nome do arquivo (sem extensão)",
            value=f"historico_viagens_{datetime.now().strftime('%Y%m%d')}"
        )

        # Botão de exportação
        if st.button(f"Exportar para {formato}"):
            extensao = formato.lower()
            caminho = f"{nome_arquivo}.{extensao}"

            resultado = self.controller.exportar_historico(formato=extensao, caminho=caminho)

            if resultado['success']:
                st.success(resultado['message'])

                # Oferecer download do arquivo
                with open(resultado['path'], "rb") as file:
                    btn = st.download_button(
                        label="Baixar arquivo",
                        data=file,
                        file_name=os.path.basename(resultado['path']),
                        mime=(
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if formato == "Excel" else
                            "application/json" if formato == "JSON" else
                            "text/csv"
                        )
                    )

                # Remover o arquivo temporário após download
                if btn:
                    os.remove(resultado['path'])
            else:
                st.error(resultado['message'])

    def _calcular_duracao(self, hora_inicio: str, hora_fim: str) -> str:
        """Calcula a duração entre duas horas."""
        if not hora_inicio or not hora_fim:
            return "N/A"

        try:
            inicio = datetime.strptime(hora_inicio, "%H:%M")
            fim = datetime.strptime(hora_fim, "%H:%M")
            diferenca = fim - inicio
            horas = diferenca.seconds // 3600
            minutos = (diferenca.seconds % 3600) // 60
            return f"{horas:02d}:{minutos:02d}"
        except:
            return "N/A"

# """
# Módulo de view para a interface do diário de bordo.
# """
#
# import streamlit as st
# import pandas as pd
# from datetime import datetime
# from controllers.viagem_controller import ViagemController
# from utils.data_utils import DataUtils
#
# class ViagemView:
#     """Classe que implementa a interface do usuário usando Streamlit."""
#
#     def __init__(self):
#         self.controller = ViagemController()
#         self._configurar_pagina()
#
#     def _configurar_pagina(self):
#         """Configurações iniciais da página."""
#         st.set_page_config(
#             page_title="Diário de Bordo",
#             page_icon="🚗",
#             layout="wide",
#             initial_sidebar_state="expanded"
#         )
#         st.title("📖 Diário de Bordo")
#
#     def _mostrar_cabecalho(self):
#         """Exibe informações no cabeçalho."""
#         st.markdown("""
#             **Registro completo de viagens**
#             *Inicie novas viagens, finalize as em andamento e consulte o histórico*
#         """)
#
#     def _mostrar_menu_lateral(self):
#         """Exibe e gerencia o menu lateral."""
#         with st.sidebar:
#             st.header("Menu")
#             return st.selectbox(
#                 "Selecione uma opção",
#                 ["Iniciar Viagem", "Finalizar Viagem", "Exibir Histórico", "Exportar Histórico"],
#                 key="menu_principal"
#             )
#
#     def _mostrar_formulario_inicio_viagem(self):
#         """Exibe o formulário para iniciar uma nova viagem."""
#         st.subheader("Iniciar Nova Viagem")
#
#         with st.form(key="form_iniciar_viagem", clear_on_submit=True):
#             col1, col2 = st.columns(2)
#
#             with col1:
#                 data = st.date_input(
#                     "Data da Viagem",
#                     datetime.now(),
#                     format="DD/MM/YYYY"
#                 ).strftime(DataUtils.FORMATO_DATA)
#
#                 horario_saida = st.text_input(
#                     "Horário de Saída (HH:MM)",
#                     value=DataUtils.hora_atual_formatada(),
#                     help="Formato 24 horas"
#                 )
#
#             with col2:
#                 km_inicial = st.number_input(
#                     "Quilometragem Inicial",
#                     min_value=0,
#                     step=1,
#                     value=0
#                 )
#
#                 destino = st.text_input(
#                     "Destino",
#                     placeholder="Digite o destino da viagem",
#                     max_chars=100
#                 )
#
#             if st.form_submit_button("Iniciar Viagem", use_container_width=True):
#                 resultado = self.controller.iniciar_viagem(data, horario_saida, km_inicial, destino)
#
#                 if resultado['success']:
#                     st.success(resultado['message'])
#                     st.balloons()
#                 else:
#                     st.error(resultado['message'])
#
#     def _mostrar_formulario_fim_viagem(self):
#         """Exibe o formulário para finalizar a viagem ativa."""
#         st.subheader("Finalizar Viagem Ativa")
#
#         if not self.controller.verificar_viagem_ativa():
#             st.info("ℹ️ Não há viagem ativa para finalizar.")
#             return
#
#         with st.form(key="form_finalizar_viagem", clear_on_submit=True):
#             col1, col2 = st.columns(2)
#
#             with col1:
#                 data = st.date_input(
#                     "Data de Chegada",
#                     datetime.now(),
#                     format="DD/MM/YYYY"
#                 ).strftime(DataUtils.FORMATO_DATA)
#
#                 horario_chegada = st.text_input(
#                     "Horário de Chegada (HH:MM)",
#                     value=DataUtils.hora_atual_formatada(),
#                     help="Formato 24 horas"
#                 )
#
#             with col2:
#                 km_final = st.number_input(
#                     "Quilometragem Final",
#                     min_value=0,
#                     step=1,
#                     value=0
#                 )
#
#             if st.form_submit_button("Finalizar Viagem", use_container_width=True):
#                 resultado = self.controller.finalizar_viagem(data, horario_chegada, km_final)
#
#                 if resultado['success']:
#                     st.success(resultado['message'])
#                     st.balloons()
#                 else:
#                     st.error(resultado['message'])
#
#     def _mostrar_historico(self):
#
#         """Exibe e permite edição do histórico de viagens."""
#         try:
#             historico = self.controller.obter_historico()
#
#             # Verificar se o histórico está vazio
#             if historico.empty if hasattr(historico, 'empty') else not historico:
#                 st.info("Nenhuma viagem registrada ainda.")
#                 return
#
#             # Converter para DataFrame se não for
#             if not isinstance(historico, pd.DataFrame):
#                 df = pd.DataFrame(historico)
#             else:
#                 df = historico.copy()
#
#             # Converter coluna de data para datetime
#             df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')
#
#             # Configuração das colunas
#             column_config = {
#                 "data": st.column_config.DateColumn(
#                     "Data",
#                     format="DD/MM/YYYY",
#                     help="Data da viagem"
#                 ),
#                 "hora_inicial": st.column_config.TextColumn(
#                     "Hora Saída",
#                     help="Formato HH:MM"
#                 ),
#                 "km_inicial": st.column_config.NumberColumn(
#                     "KM Inicial",
#                     format="%d",
#                     step=1
#                 ),
#                 "hora_final": st.column_config.TextColumn(
#                     "Hora Chegada",
#                     help="Formato HH:MM"
#                 ),
#                 "km_final": st.column_config.NumberColumn(
#                     "KM Final",
#                     format="%d",
#                     step=1
#                 ),
#                 "destino": st.column_config.TextColumn(
#                     "Destino"
#                 ),
#                 "total_km": st.column_config.NumberColumn(
#                     "KM Percorridos",
#                     disabled=True
#                 ),
#                 "tempo_levado": st.column_config.TextColumn(
#                     "Duração",
#                     disabled=True
#                 )
#             }
#
#             # Exibir editor de dados
#             edited_df = st.data_editor(
#                 df,
#                 column_config=column_config,
#                 use_container_width=True,
#                 num_rows="dynamic",
#                 key="editor_historico"
#             )
#
#             if st.button("Salvar Alterações"):
#                 # Converter data de volta para string no formato original
#                 edited_df['data'] = edited_df['data'].dt.strftime('%d/%m/%Y')
#
#                 # Enviar dados atualizados para o controller
#                 resultado = self.controller.atualizar_historico(edited_df)
#
#                 if resultado['success']:
#                     st.success("Histórico atualizado com sucesso!")
#                     st.rerun()
#                 else:
#                     st.error(f"Erro ao salvar: {resultado['message']}")
#
#         except Exception as e:
#             st.error(f"Erro ao processar histórico: {str(e)}")
#
#     def _mostrar_exportacao(self):
#         """Exibe a interface para exportar o histórico."""
#         st.subheader("Exportar Histórico")
#
#         caminho = st.text_input(
#             "Caminho do arquivo Excel",
#             value="historico_viagens.xlsx",
#             help="Caminho onde o arquivo será salvo"
#         )
#
#         if st.button("Exportar para Excel", use_container_width=True):
#             with st.spinner("Exportando dados..."):
#                 resultado = self.controller.exportar_historico(caminho)
#
#             if resultado['success']:
#                 st.success(resultado['message'])
#                 st.download_button(
#                     label="Baixar Arquivo",
#                     data=open(caminho, "rb").read(),
#                     file_name=caminho,
#                     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#                     use_container_width=True
#                 )
#             else:
#                 st.error(resultado['message'])
#
#     def executar(self):
#         """Método principal para execução da interface."""
#         self._mostrar_cabecalho()
#         opcao_selecionada = self._mostrar_menu_lateral()
#
#         if opcao_selecionada == "Iniciar Viagem":
#             self._mostrar_formulario_inicio_viagem()
#         elif opcao_selecionada == "Finalizar Viagem":
#             self._mostrar_formulario_fim_viagem()
#         elif opcao_selecionada == "Exibir Histórico":
#             self._mostrar_historico()
#         elif opcao_selecionada == "Exportar Histórico":
#             self._mostrar_exportacao()