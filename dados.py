import os
import pandas as pd
import numpy as np
import streamlit as st
from config import CAMINHO_DADOS, CAMINHO_PLANILHA
import logging

def carregar_dados():
    try:
        if os.path.exists(CAMINHO_DADOS):
            df = pd.read_json(CAMINHO_DADOS)
        else:
            df = pd.read_excel(CAMINHO_PLANILHA, sheet_name="AÇÕES", header=1)
            df = df.dropna(how="all").reset_index(drop=True)
            colunas_renomeadas = {
                "PAPEL": "Papel", "EMPRESA": "Empresa", "P MÉD": "Preço Médio",
                "P ATUAL $": "Preço Atual", "P TETO $": "Preço Teto",
                "TOTAL": "Quantidade", "APORTADO": "Total Investido",
                "ATUAL": "Valor Atual", "TOTAIS": "Dividendos",
                "POR AÇÃO": "Dividendos/Ação", "TOTAL %": "Rentabilidade"
            }
            df = df.rename(columns=colunas_renomeadas)
            df = df[list(colunas_renomeadas.values())].copy()
            df.to_json(CAMINHO_DADOS, orient="records", indent=2)

        df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").fillna(0).astype(int)
        df["Total Investido"] = pd.to_numeric(df["Total Investido"], errors="coerce").fillna(0)
        df["Preço Atual"] = np.nan
        df["Valor Atual"] = 0
        df["Rentabilidade"] = 0.0
        df["PT Bazin"] = pd.to_numeric(df["Dividendos/Ação"], errors="coerce") * (100 / 6)
        df["PT Bazin"] = df["PT Bazin"].round(2)

        return df
    except Exception as e:
        logging.critical(f"Erro ao carregar dados: {str(e)}", exc_info=True)
        st.error(f"❌ Falha ao carregar dados: {str(e)}")
        raise

def salvar_dados(df):
    try:
        df.to_json(CAMINHO_DADOS, orient="records", indent=2)
        logging.info("Dados salvos com sucesso")
        st.success("💾 Dados salvos com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao salvar dados: {str(e)}", exc_info=True)
        st.error(f"❌ Falha ao salvar dados: {str(e)}")

def atualizar_dados_financeiros(df, cache):
    for idx, row in df.iterrows():
        papel = row["Papel"]
        ticker = f"{papel}.SA" if not str(papel).endswith(".SA") else papel
        try:
            cotacao = cache.obter_cotacao(ticker)
            if cotacao and cotacao['preco']:
                preco_atual = cotacao['preco']
                df.at[idx, "Preço Atual"] = preco_atual
                df.at[idx, "Valor Atual"] = round(row["Quantidade"] * preco_atual, 2)
                if row["Total Investido"] > 0:
                    rentabilidade = ((df.at[idx, "Valor Atual"] - row["Total Investido"]) / row["Total Investido"]) * 100
                    df.at[idx, "Rentabilidade"] = round(rentabilidade, 2)
        except Exception as e:
            logging.error(f"Erro ao atualizar {ticker}: {str(e)}")
    return df
