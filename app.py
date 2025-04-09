import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# Configuração inicial da página
st.set_page_config(
    page_title="Análise de Ações - Warren Buffet",
    page_icon="📈",
    layout="wide"
)

# Funções auxiliares
@st.cache_data(ttl=3600)  # Cache por 1 hora
def buscar_dados(ticker, start_date, end_date):
    try:
        dados = yf.download(ticker + '.SA', start=start_date, end=end_date)
        if dados.empty:
            st.error("Nenhum dado encontrado para este período.")
            return None
        return dados
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return None

def calcular_variacao(dados):
    if len(dados) < 2:
        return 0
    primeiro = dados['Close'].iloc[0]
    ultimo = dados['Close'].iloc[-1]
    return ((ultimo - primeiro) / primeiro) * 100

def mostrar_analise(dados, ticker):
    if dados is None:
        return
    
    st.subheader(f"Análise: {ticker}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Preço Atual", f"R$ {dados['Close'].iloc[-1]:.2f}")
    with col2:
        variacao_periodo = calcular_variacao(dados)
        st.metric("Variação no Período", f"{variacao_periodo:.2f}%")
    with col3:
        st.metric("Volume Médio", f"{dados['Volume'].mean():,.0f}")
    
    tab1, tab2, tab3 = st.tabs(["Gráfico", "Últimos Registros", "Análise Técnica"])
    
    with tab1:
        st.line_chart(dados['Close'], use_container_width=True)
    
    with tab2:
        st.dataframe(dados.tail(10).sort_index(ascending=False))
    
    with tab3:
        st.write("📉 Indicadores técnicos (em desenvolvimento)")
        # Futuro: adicionar médias móveis, RSI etc.

# Sidebar com controles
with st.sidebar:
    st.header("Configurações")
    
    ticker = st.selectbox(
        "Selecione a ação:",
        ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'BBAS3', 'ABEV3'],
        index=0
    )
    
    hoje = datetime.today()
    ontem = hoje - timedelta(days=1)
    padrao_inicio = hoje - timedelta(days=30)

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Data inicial:",
            value=padrao_inicio,
            max_value=ontem
        )
    with col2:
        end_date = st.date_input(
            "Data final:",
            value=ontem,
            max_value=ontem
        )

    if start_date >= end_date:
        st.error("A data inicial deve ser anterior à data final!")
        st.stop()

# Corpo principal
with st.spinner(f"Carregando dados de {ticker}..."):
    dados = buscar_dados(ticker, start_date, end_date)

if dados is not None:
    mostrar_analise(dados, ticker)

    st.divider()
    st.subheader("📊 Dados Estatísticos")
    st.write(dados.describe())

    st.download_button(
        label="⬇️ Baixar dados em CSV",
        data=dados.to_csv().encode('utf-8'),
        file_name=f"{ticker}_dados.csv",
        mime="text/csv"
    )
