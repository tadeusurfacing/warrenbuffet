import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from dados import carregar_dados, atualizar_dados_financeiros, salvar_dados
from cotacoes import CotacaoCache
from utils import formatar_valores
from relatorio import exportar_pdf

st.set_page_config(page_title="Monitor de Investimentos", layout="wide")
st.title("📊 Monitor de Investimentos")

st.title("📊 Monitor de Investimentos")

# Inicializar cache e carregar dados
cache = CotacaoCache()
df = carregar_dados()

# 🧼 Limpeza: remover espaços e padronizar códigos dos ativos
df["Papel"] = df["Papel"].astype(str).str.strip().str.upper()

# 🗑️ Excluir linhas 21 e 22 (índices 20 e 21)
df = df.drop(index=[20, 21], errors="ignore")

# ✅ Atualizar cotações automaticamente (uma vez por sessão)
if "cotacoes_atualizadas" not in st.session_state:
    df = atualizar_dados_financeiros(df, cache)
    st.session_state["cotacoes_atualizadas"] = True

# Sidebar
st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Ir para:", ["Ações", "Gráficos", "Análise Geral"])

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Atualizar Cotações"):
    df = atualizar_dados_financeiros(df, cache)
    st.session_state["cotacoes_atualizadas"] = True
    st.success("Cotações atualizadas!")

if st.sidebar.button("💾 Salvar Dados"):
    salvar_dados(df)

if st.sidebar.button("📄 Exportar PDF"):
    exportar_pdf(df)

# Página: Tabela de Ações
if pagina == "Ações":
    st.subheader("📋 Tabela de Ações")
    df_formatado = df.apply(formatar_valores, axis=1)
    st.dataframe(df_formatado, use_container_width=True)

# Página: Gráficos
elif pagina == "Gráficos":
    st.subheader("📈 Rentabilidade por Ativo")
    fig1, ax1 = plt.subplots()
    df.plot.bar(x="Papel", y="Rentabilidade", ax=ax1, color="skyblue")
    st.pyplot(fig1)

    st.subheader("📊 Distribuição da Carteira")
    fig2, ax2 = plt.subplots()
    df.plot.pie(y="Valor Atual", labels=df["Papel"], ax=ax2, autopct="%1.1f%%")
    ax2.set_ylabel("")
    st.pyplot(fig2)

# Página: Análise Geral
elif pagina == "Análise Geral":
    st.subheader("📊 Análise Geral da Carteira")
    total_investido = df["Total Investido"].sum()
    valor_atual = df["Valor Atual"].sum()
    rentabilidade_media = df["Rentabilidade"].mean()
    positivos = df[df["Rentabilidade"] > 0].shape[0]
    negativos = df[df["Rentabilidade"] <= 0].shape[0]
    top_rent = df.sort_values("Rentabilidade", ascending=False).head(3)[["Papel", "Rentabilidade"]]
    top_div = df.sort_values("Dividendos", ascending=False).head(3)[["Papel", "Dividendos"]]

    st.markdown(f"""
    **Total Investido**: R$ {total_investido:,.2f}  
    **Valor Atual**: R$ {valor_atual:,.2f}  
    **Rentabilidade Média**: {rentabilidade_media:.2f}%  
    **Ativos Positivos**: {positivos} | **Negativos**: {negativos}
    """)

    st.markdown("#### 🥇 Top Rentabilidade")
    st.table(top_rent)

    st.markdown("#### 💵 Top Dividendos")
    st.table(top_div)
