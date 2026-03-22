import os
import oracledb
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import datetime
import plotly.graph_objects as go

# 1. Higiene Digital: Carregamento no escopo global
load_dotenv()

# --- 1. INFRAESTRUTURA DE BANCO DE DADOS (POOL) ---
@st.cache_resource
def iniciar_pool_banco():
    try:
        pool = oracledb.create_pool(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            dsn=os.getenv("DB_DSN"),
            min=2, max=5, increment=1
        )
        return pool
    except Exception as erro:
        st.error(f"Erro fatal ao criar Pool: {erro}")
        return None

pool_oracle = iniciar_pool_banco()

# --- 2. FUNÇÕES DE DADOS PROTEGIDAS (COM JOIN MULTI-MOEDAS) ---
@st.cache_data(ttl="1h")
def calcular_kpis(d_inicio, d_fim, nome_moeda):
    if not pool_oracle:
        return 0.0, 0.0, 0.0
    try:
        conexao = pool_oracle.acquire()
        cursor = conexao.cursor()
        
        # O JOIN cruza a tabela fato (Cotação) com a dimensão (Moeda)
        comando_sql = """
            SELECT 
                AVG(c.PRECO_COMPRA) AS TWAP_COMPRA,
                AVG(c.PRECO_VENDA) AS TWAP_VENDA,
                SUM(c.PRECO_COMPRA * c.VOLUME) / NULLIF(SUM(c.VOLUME), 0) AS VWAP_COMPRA
            FROM TB_COTACAO c
            JOIN TB_MOEDA m ON c.ID_MOEDA = m.ID_MOEDA
            WHERE m.NOME_MOEDA = :1 
              AND c.DATA_COTACAO BETWEEN TO_DATE(:2, 'YYYY-MM-DD') AND TO_DATE(:3, 'YYYY-MM-DD')
        """
        cursor.execute(comando_sql, [nome_moeda, d_inicio.strftime('%Y-%m-%d'), d_fim.strftime('%Y-%m-%d')])
        media_compra, media_venda, vwap_compra = cursor.fetchone()
        return media_compra or 0.0, media_venda or 0.0, vwap_compra or 0.0
        
    except Exception as erro:
        st.error(f"Falha ao calcular KPIs: {erro}")
        return 0.0, 0.0, 0.0
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexao' in locals(): pool_oracle.release(conexao)

@st.cache_data(ttl="1h")
def buscar_historico(d_inicio, d_fim, nome_moeda):
    if not pool_oracle:
        return []
    try:
        conexao = pool_oracle.acquire()
        cursor = conexao.cursor()
        
        comando_sql = """
            SELECT c.DATA_COTACAO, c.PRECO_COMPRA 
            FROM TB_COTACAO c
            JOIN TB_MOEDA m ON c.ID_MOEDA = m.ID_MOEDA
            WHERE m.NOME_MOEDA = :1 
              AND c.DATA_COTACAO BETWEEN TO_DATE(:2, 'YYYY-MM-DD') AND TO_DATE(:3, 'YYYY-MM-DD')
            ORDER BY c.DATA_COTACAO ASC
        """
        cursor.execute(comando_sql, [nome_moeda, d_inicio.strftime('%Y-%m-%d'), d_fim.strftime('%Y-%m-%d')])
        return cursor.fetchall()
        
    except Exception as erro:
        st.error(f"Falha ao buscar histórico: {erro}")
        return []
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexao' in locals(): pool_oracle.release(conexao)

# --- 3. CONFIGURAÇÃO DA INTERFACE (FRONTEND) ---
st.title("Dashboard Financeiro Macro")

with st.expander("📚 Entenda os Indicadores e o Comportamento do Gráfico"):
    st.markdown("""
    **1. Métricas de Execução (Preço Médio):**
    * **TWAP (Média no Tempo):** Calcula a cotação média do período ignorando distorções momentâneas.
    * **VWAP (Média pelo Volume):** Mostra o "preço justo" onde a maior parte do dinheiro institucional realmente trocou de mãos.

    **2. Leitura de Volatilidade e Cores (Regra Macroeconômica):**
    Diferente do mercado de ações, no câmbio nós analisamos o impacto na *nossa* economia (o Real). Portanto, as cores são invertidas:
    * 🟢 **Barras Verdes (Moeda em Queda):** Cenário **positivo**. Significa que o Real se valorizou, barateando importações e aliviando a inflação.
    * 🔴 **Barras Vermelhas (Moeda em Alta):** Cenário **negativo**. Significa que o Real perdeu força, encarecendo produtos cotados em moeda estrangeira e gerando pressão inflacionária.
    """)

# Menu Lateral (Sidebar)
st.sidebar.header("Filtros de Análise")

moeda_selecionada = st.sidebar.selectbox(
    'Selecione o Indicador:', 
    ('Dólar', 'Euro'),
    help="Alterne entre as moedas armazenadas no banco de dados normalizado."
)

hoje = datetime.date.today()
trinta_dias_atras = hoje - datetime.timedelta(days=30)

data_selecionada = st.sidebar.date_input(
    "Período de análise:",
    value=(trinta_dias_atras, hoje),
    max_value=hoje
)

# Renderização Principal Dinâmica (Aceita qualquer moeda!)
if len(data_selecionada) == 2:
    data_inicio, data_fim = data_selecionada

    # A variável 'moeda_selecionada' viaja do menu lateral direto para a Query SQL
    dados_historicos = buscar_historico(data_inicio, data_fim, moeda_selecionada)
    
    if dados_historicos:
        df_historico = pd.DataFrame(dados_historicos, columns=["Data", "Preço Diário"])
        df_historico["Data"] = pd.to_datetime(df_historico["Data"])
        df_historico.set_index("Data", inplace=True)
        
        preco_inicio = df_historico['Preço Diário'].iloc[0]
        preco_fim = df_historico['Preço Diário'].iloc[-1]
        variacao_periodo = preco_fim - preco_inicio

        st.write(f"### Desempenho do Período ({data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}) - {moeda_selecionada}")
        compra_twap, venda_twap, vwap_compra = calcular_kpis(data_inicio, data_fim, moeda_selecionada)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Média de Compra (TWAP)", f"R$ {compra_twap:.4f}", delta=f"R$ {variacao_periodo:.4f} no período", delta_color="inverse")
        col2.metric("Média de Venda (TWAP)", f"R$ {venda_twap:.4f}")
        col3.metric("Preço Ponderado (VWAP)", f"R$ {vwap_compra:.4f}")
            
        st.markdown("---")

        st.write(f"### Volatilidade: Ganhos e Perdas Diárias ({moeda_selecionada})")
        
        df_historico['Variação (R$)'] = df_historico['Preço Diário'].diff()
        
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_historico.index,
            y=df_historico['Variação (R$)'],
            marker_color=['#ff4b4b' if val > 0 else '#00b050' for val in df_historico['Variação (R$)']],
            name="Variação Diária"
        ))

        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=20, b=0),
            yaxis=dict(
                showgrid=True, gridcolor="rgba(200, 200, 200, 0.2)", 
                zeroline=True, zerolinecolor="rgba(255, 255, 255, 0.5)", zerolinewidth=2
            ),
            showlegend=False,
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("Ver Base de Dados Completa"):
            st.dataframe(df_historico, use_container_width=True)
    else:
        st.info(f"Nenhum dado encontrado para {moeda_selecionada} no período selecionado.")
else:
    st.info("Por favor, selecione uma data de início e de fim no calendário lateral para gerar a análise.")