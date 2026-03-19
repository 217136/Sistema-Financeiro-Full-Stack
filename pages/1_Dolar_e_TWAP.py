import os
import oracledb
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# --- 1. CONFIGURAÇÃO DA INTERFACE (UI) ---
st.title("Dashboard Financeiro Macro")
st.write("Monitoramento avançado de Preço Médio Ponderado no Tempo (TWAP) e Tendência Histórica.")

# --- 2. BACKEND E CACHE DE DADOS ---

# 2.1 Função protegida por Cache para a Matemática do TWAP
@st.cache_data
def calcular_twap():
    load_dotenv()
    try:
        conexao = oracledb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            dsn=os.getenv("DB_DSN")
        )
        cursor = conexao.cursor()
        
        comando_sql = """
            SELECT 
                AVG(PRECO_COMPRA) AS MEDIA_COMPRA, 
                AVG(PRECO_VENDA) AS MEDIA_VENDA 
            FROM TB_COTACAO_DOLAR
        """
        cursor.execute(comando_sql)
        media_compra, media_venda = cursor.fetchone()
        
        # Higiene Digital
        cursor.close()
        conexao.close()
        return media_compra, media_venda
        
    except Exception as erro:
        st.write("Falha na operação de cálculo. Erro:", erro)
        return 0.0, 0.0

# 2.2 Função protegida por Cache para a Série Histórica (Gráfico)
@st.cache_data
def buscar_historico():
    load_dotenv()
    try:
        conexao = oracledb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            dsn=os.getenv("DB_DSN")
        )
        cursor = conexao.cursor()
        
        # A cláusula ORDER BY ASC garante a ordenação cronológica do gráfico
        comando_sql = """
            SELECT DATA_COTACAO, PRECO_COMPRA 
            FROM TB_COTACAO_DOLAR 
            ORDER BY DATA_COTACAO ASC
        """
        cursor.execute(comando_sql)
        
        # Usamos fetchall() para extrair todas as linhas de histórico
        resultado = cursor.fetchall()
        
        cursor.close()
        conexao.close()
        return resultado
        
    except Exception as erro:
        st.write("Falha ao buscar histórico. Erro:", erro)
        return []

# --- 3. EXIBIÇÃO DE DADOS (FRONTEND E WIDGETS) ---

# O widget selectbox cria o menu interativo
moeda_selecionada = st.selectbox('Selecione o Indicador Macro:', ('Dólar', 'Euro'))

# Lógica de Negócio Dinâmica
if moeda_selecionada == 'Dólar':
    
    # 3.1 Exibição dos KPIs Financeiros (Métricas)
    compra_twap, venda_twap = calcular_twap()
    
    # Organizando as métricas lado a lado usando st.columns (Boas práticas de UI)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Média Ponderada de Compra (TWAP)", value=f"R$ {compra_twap:.4f}")
    with col2:
        st.metric(label="Média Ponderada de Venda (TWAP)", value=f"R$ {venda_twap:.4f}")
        
    # 3.2 Processamento e Exibição do Gráfico de Linha
    st.write("### Tendência Histórica (Preço de Compra)")
    dados_historicos = buscar_historico()
    
    if dados_historicos:
        # Transformação estrutural em um DataFrame do Pandas
        df_historico = pd.DataFrame(dados_historicos, columns=["Data", "Preço de Compra"])
        
        # Definimos a Data como índice para que o eixo X do gráfico fique correto
        df_historico.set_index("Data", inplace=True)
        
        # Renderização do Gráfico Nativo
        st.line_chart(df_historico)

else:
    # Tratamento para dados inexistentes
    st.warning("Aviso: Dados de Euro ainda não integrados na base Oracle Cloud.")