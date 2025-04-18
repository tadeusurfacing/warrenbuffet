import os
import pandas as pd
import numpy as np
import logging

from config import CAMINHO_DADOS, CAMINHO_PLANILHA

def carregar_dados():
    """
    Carrega os dados de um arquivo JSON ou Excel.
    Retorna: DataFrame com os dados.
    """
    try:
        if False and os.path.exists(CAMINHO_DADOS):
            df = pd.read_json(CAMINHO_DADOS)
        else:
            df = pd.read_excel(CAMINHO_PLANILHA, sheet_name="AÇÕES", header=1)
            df = df.dropna(how="all").reset_index(drop=True)
            colunas_renomeadas = {
                "PAPEL": "Papel",
                "EMPRESA": "Empresa",
                "P MÉD": "Preço Médio",
                "P ATUAL $": "Preço Atual",
                # "P TETO $": "Preço Teto",  # Removida a coluna "Preço Teto"
                "TOTAL": "QTD",  # Alterado de "Quantidade" para "QTD"
                "APORTADO": "Total Investido",
                "ATUAL": "Valor Atual",
                "TOTAIS": "Dividendos",
                "POR AÇÃO": "DIV/Ação",  # Alterado de "Dividendos/Ação" para "DIV/Ação"
                "TOTAL %": "Rentabilidade"
            }
            df = df.rename(columns=colunas_renomeadas)
            df = df[list(colunas_renomeadas.values())].copy()  # Exclui colunas não listadas, como "Preço Teto"
            df.to_json(CAMINHO_DADOS, orient="records", indent=2)

        df["QTD"] = pd.to_numeric(df["QTD"], errors="coerce").fillna(0).astype(int)
        df["Total Investido"] = pd.to_numeric(df["Total Investido"], errors="coerce").fillna(0)
        df["Preço Atual"] = np.nan
        df["Valor Atual"] = 0
        df["Rentabilidade"] = 0.0
        df["PT Bazin"] = pd.to_numeric(df["DIV/Ação"], errors="coerce") * (100 / 6)
        df["PT Bazin"] = df["PT Bazin"].round(2)

        return df
    except Exception as e:
        logging.critical(f"Erro ao carregar dados: {str(e)}", exc_info=True)
        raise Exception(f"❌ Falha ao carregar dados: {str(e)}")

def salvar_dados(df):
    """
    Salva os dados do DataFrame em um arquivo JSON.
    df: DataFrame com os dados.
    Retorna: Uma tupla (sucesso, mensagem).
    """
    try:
        df.to_json(CAMINHO_DADOS, orient="records", indent=2)
        logging.info("Dados salvos com sucesso")
        return True, "💾 Dados salvos com sucesso!"
    except Exception as e:
        logging.error(f"Erro ao salvar dados: {str(e)}", exc_info=True)
        return False, f"❌ Falha ao salvar dados: {str(e)}"

def atualizar_dados_financeiros(df, cache):
    """
    Atualiza os dados financeiros no DataFrame usando o cache.
    df: DataFrame com os dados.
    cache: Objeto de cache para cotações.
    Retorna: DataFrame atualizado.
    """
    for idx, row in df.iterrows():
        papel = row["Papel"]
        ticker = f"{papel}.SA" if not str(papel).endswith(".SA") else papel
        try:
            cotacao = cache.obter_cotacao(ticker)
            if cotacao and cotacao['preco']:
                preco_atual = cotacao['preco']
                df.at[idx, "Preço Atual"] = preco_atual
                df.at[idx, "Valor Atual"] = round(row["QTD"] * preco_atual, 2)
                if row["Total Investido"] > 0:
                    rentabilidade = ((df.at[idx, "Valor Atual"] - row["Total Investido"]) / row["Total Investido"]) * 100
                    df.at[idx, "Rentabilidade"] = round(rentabilidade, 2)
        except Exception as e:
            logging.error(f"Erro ao atualizar {ticker}: {str(e)}")
    return df
