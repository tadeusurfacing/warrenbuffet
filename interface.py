import os
import json
import streamlit as st
import pandas as pd
import numpy as np
import threading

from utils import formatar_valores
from graficos import atualizar_graficos, atualizar_analise
from relatorio import exportar_pdf
from dados import carregar_dados, atualizar_dados_financeiros, salvar_dados

# Inicializar o DataFrame no session_state
if "df" not in st.session_state:
    try:
        st.session_state["df"] = carregar_dados()
    except Exception as e:
        st.error(str(e))
        st.session_state["df"] = pd.DataFrame()

def iniciar_interface(df, cache):
    try:
        with open("config_colunas.json", "r", encoding="utf-8") as f:
            col_widths = json.load(f)
    except Exception:
        col_widths = {
            "Papel": 70,
            "Empresa": 140,
            "Preço Médio": 80,
            "Preço Atual": 80,
            "Quantidade": 70,
            "Total Investido": 100,
            "Valor Atual": 100,
            "Dividendos": 90,
            "Dividendos/Ação": 90,
            "Rentabilidade": 90,
            "PT Bazin": 80
        }

    st.title("Monitor de Investimentos")

    with st.sidebar:
        st.header("Ações")

        if st.button("💾 Salvar"):
            sucesso, mensagem = salvar_dados(st.session_state["df"])
            if sucesso:
                st.success(mensagem)
            else:
                st.error(mensagem)

        if st.button("📄 Exportar PDF"):
            sucesso, mensagem = exportar_pdf(st.session_state["df"])
            if sucesso:
                st.success(mensagem)
            else:
                st.error(mensagem)

        def inicializar_precos():
            status_placeholder = st.empty()
            status_placeholder.info("Atualizando cotações...")
            try:
                st.session_state["df"] = atualizar_dados_financeiros(st.session_state["df"], cache)
                status_placeholder.success("Cotações atualizadas!")
            except Exception as e:
                status_placeholder.error(f"Erro ao atualizar cotações: {str(e)}")

        if st.button("🔄 Atualizar Cotações"):
            threading.Thread(target=inicializar_precos, daemon=True).start()

    tab_names = ["Ações", "Gráficos", "Análise Geral"]
    tabs = st.tabs(tab_names)

    with tabs[0]:
        colunas_para_mostrar = list(col_widths.keys())
        df_exibicao = st.session_state["df"].apply(formatar_valores, axis=1)
        df_exibicao = df_exibicao[colunas_para_mostrar]
        st.dataframe(
            df_exibicao,
            use_container_width=True,
            column_config={col: st.column_config.Column(width=col_widths.get(col, 80)) for col in colunas_para_mostrar}
        )

    with tabs[1]:
        graficos_placeholder = st.empty()
        atualizar_graficos(graficos_placeholder, st.session_state["df"])

    with tabs[2]:
        analise_placeholder = st.empty()
        atualizar_analise(analise_placeholder, st.session_state["df"])

    status_var = st.session_state.get("status", "Pronto")
    st.info(f"Status: {status_var}")

if "status" not in st.session_state:
    st.session_state["status"] = "Pronto"