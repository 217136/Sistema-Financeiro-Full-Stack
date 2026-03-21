import os
import oracledb
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import datetime

# --- 1. CONFIGURAÇÃO DA INTERFACE (UI E CONTEXTO) ---
st.title("Dashboard Financeiro Macro")

# Boa prática de UI/UX: Explicando os indicadores usando Markdown
st.markdown("""
**Contexto dos Indicadores:**
*   **TWAP (Time-Weighted Average Price):** Preço médio ponderado no tempo. Filtra as flutuações e ruídos da cotação ao longo de um período.
*   **VWAP (Volume-Weighted Average Price):** Preço médio ponderado pelo volume. *Em breve: exigirá atualização do pipeline de ETL para captura de volumetria.*
---
""")

# --- 2. INTERATIVIDADE E FILTROS (WIDGETS) ---
st.sidebar.header("Painel de Controle")
moeda_selecionada = st.sidebar.selectbox('Selecione o Indicador Macro:', ('Dólar', 'Euro'))

# Lógica de datas padrão (Últimos 30 dias)
hoje = datetime.date.today()
trinta_dias_atras = hoje - datetime.timedelta(days=30)

# Widget de calendário para selecionar a faixa de datas
data_selecionada = st.sidebar.date_input(
    "Selecione o período de análise:",
    value=(trinta_dias_atras, hoje),
    max_value=hoje
)

# --- 3. BACKEND E CACHE DE DADOS ---
# O Cache agora entende que, se as datas mudarem, ele deve buscar novos dados no banco
@st.cache_data
def calcular_kpis(d_inicio, d_fim):
    load_dotenv()
    try:
        conexao = oracledb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            dsn=os.getenv("DB_DSN")
        )
        cursor = conexao.cursor()
        
        # Uso rigoroso de Bind Variables (:data_inicio e :data_fim) para Segurança e Performance
        comando_sql = """
            SELECT 
                AVG(PRECO_COMPRA) AS TWAP_COMPRA, 
                AVG(PRECO_VENDA) AS TWAP_VENDA 
            FROM TB_COTACAO_DOLAR
            WHERE DATA_COTACAO BETWEEN :data_inicio AND :data_fim
        """
        
        # Injetando as variáveis de forma segura no Oracle
        cursor.execute(comando_sql, data_inicio=d_inicio, data_fim=d_fim)
        media_compra, media_venda = cursor.fetchone()
        
        cursor.close()
        conexao.close()
        
        # Tratamento contra valores nulos caso o período selecionado não tenha pregão
        return media_compra or 0.0, media_venda or 0.0
        
    except Exception as erro:
        st.error(f"Falha na operação de cálculo. Erro: {erro}")
        return 0.0, 0.0

@st.cache_data
def buscar_historico(d_inicio, d_fim):
    load_dotenv()
    try:
        conexao = oracledb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            dsn=os.getenv("DB_DSN")
        )
        cursor = conexao.cursor()
        
        # Cláusula WHERE com Bind Variables por Posição (:1 e :2) e Ordenação Cronológica
        comando_sql = """
            SELECT DATA_COTACAO, PRECO_COMPRA 
            FROM TB_COTACAO_DOLAR 
            WHERE DATA_COTACAO BETWEEN :1 AND :2
            ORDER BY DATA_COTACAO ASC
        """
        cursor.execute(comando_sql, [d_inicio, d_fim])
        resultado = cursor.fetchall()
        
        cursor.close()
        conexao.close()
        return resultado
        
    except Exception as erro:
        st.error(f"Falha ao buscar histórico. Erro: {erro}")
        return []

# --- 4. EXIBIÇÃO DE DADOS E LÓGICA DE NEGÓCIO ---

# Verifica se o usuário selecionou o range completo de datas (início e fim)
if len(data_selecionada) == 2:
    data_inicio, data_fim = data_selecionada

    if moeda_selecionada == 'Dólar':
        
        # 4.1 KPIs Dinâmicos
        compra_twap, venda_twap = calcular_kpis(data_inicio, data_fim)
        
        st.write(f"### Indicadores do Período ({data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')})")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Média de Compra (TWAP)", value=f"R$ {compra_twap:.4f}")
        with col2:
            st.metric(label="Média de Venda (TWAP)", value=f"R$ {venda_twap:.4f}")
            
        # 4.2 Gráfico de Evolução Filtrado
        st.write("### Tendência Histórica (Preço de Compra)")
        dados_historicos = buscar_historico(data_inicio, data_fim)
        
        if dados_historicos:
            df_historico = pd.DataFrame(dados_historicos, columns=["Data", "Preço de Compra"])
            df_historico.set_index("Data", inplace=True)
            st.line_chart(df_historico)
        else:
            st.info("Nenhum dado encontrado para o período selecionado.")

    else:
        st.warning("Aviso: Dados de Euro ainda não integrados na base Oracle Cloud.")
else:
    st.info("Por favor, selecione uma data de início e de fim no calendário lateral para gerar a análise.")