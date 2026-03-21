import os
import oracledb
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# --- 1. CONFIGURAÇÃO DA INTERFACE ---
st.title("Visão Macroeconômica Integrada")
st.write("Cruzamento Relacional: Dólar, Selic e Boletim FOCUS")

# --- 2. BACKEND E CACHE DE DADOS ---
# O decorador protege o banco Oracle contra requisições redundantes [11]
@st.cache_data
def buscar_dados_macro():
    # Higiene Digital: Carregamento seguro das credenciais [16]
    load_dotenv()
    try:
        conexao = oracledb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            dsn=os.getenv("DB_DSN")
        )
        cursor = conexao.cursor()

        # A sua consulta relacional (com a adição da ordenação cronológica)
        comando_sql = """
            SELECT 
                d.DATA_COTACAO, 
                d.PRECO_COMPRA, 
                s.VALOR_META_SELIC, 
                f.VALOR_EXPECTATIVA 
            FROM TB_COTACAO_DOLAR d 
            JOIN TB_TAXA_SELIC s ON d.DATA_COTACAO = s.DATA_REFERENCIA 
            JOIN TB_BOLETIM_FOCUS f ON d.DATA_COTACAO = f.DATA_REFERENCIA
            ORDER BY d.DATA_COTACAO ASC
        """
        cursor.execute(comando_sql)
        resultado = cursor.fetchall()

        # Higiene Digital: Encerramento de conexões
        cursor.close()
        conexao.close()
        return resultado

    except Exception as erro:
        st.write("Falha na integração de dados. Erro:", erro)
        return []

# --- 3. EXIBIÇÃO DE DADOS (FRONTEND) ---
dados_macro = buscar_dados_macro()

if dados_macro:
    # Transformação estrutural em um DataFrame do Pandas
    df_macro = pd.DataFrame(
        dados_macro, 
        columns=["Data", "Dólar (Compra)", "Meta Selic", "Expectativa Focus"]
    )

    # Definimos a Data como índice estrutural para o eixo X do gráfico
    df_macro.set_index("Data", inplace=True)

    # Renderização de Gráfico de Linhas Nativo para Séries Temporais
    st.write("### Evolução Histórica")
    st.line_chart(df_macro)

    # Renderização da Tabela Interativa
    st.write("### Base de Dados Unificada")
    st.dataframe(df_macro)
else:
    st.warning("Aviso: Nenhum dado foi encontrado no banco de dados.")