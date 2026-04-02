import os
import oracledb
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Higiene Digital
load_dotenv()

# --- 1. CONFIGURAÇÃO DA INTERFACE ---
st.title("Visão Macroeconômica Integrada")
st.write("(Cruzamento Relacional: Câmbio, Selic e Boletim FOCUS)")

with st.expander("📚 Entenda a Relação: Câmbio, Juros e Expectativas"):
    st.markdown("""
    **Os Três Pilares da Análise:** 
    * 💵 **Câmbio (Dólar/Euro):** Preço da moeda estrangeira. Sofre variação diária constante guiada pelo mercado global e fluxo de capital.
    * 🏦 **Taxa Selic (Juros):** Taxa básica da economia definida pelo Banco Central (Copom) a cada 45 dias para tentar controlar a inflação.
    * 🔮 **Boletim Focus (Expectativas):** Pesquisa semanal oficial que mostra a projeção mediana do mercado financeiro para onde a Selic vai parar no fim do ano.

    **Como interpretar o gráfico? (A Dinâmica Macro)**
    Na teoria econômica, existe um efeito de "gangorra" entre essas variáveis:
    Quando o Banco Central **sobe a Selic**, o país atrai mais capital estrangeiro (investidores buscando altos rendimentos na renda fixa). A entrada massiva dessa moeda no Brasil aumenta a oferta e tende a **fazer a cotação cair** (e vice-versa).
    
    *Nota de Limpeza Visual: O gráfico exibe as linhas suavizadas pela **Média Mensal**. Isso remove o "ruído" das oscilações frenéticas do dia a dia e revela a tendência real e histórica da nossa economia.*
    """)

# Menu Lateral (Filtro de Moeda)
st.sidebar.header("Parâmetros Macro")
moeda_selecionada = st.sidebar.selectbox(
    'Selecione a Moeda de Comparação:', 
    ('Dólar', 'Euro')
)

# --- 2. BACKEND E INFRAESTRUTURA DE DADOS ---
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
        st.error(f"Erro fatal ao criar Pool de Conexões: {erro}")
        return None

pool_oracle = iniciar_pool_banco()

@st.cache_data(ttl="1h")
def buscar_dados_macro(nome_moeda):
    if not pool_oracle:
        return []
        
    try:
        conexao = pool_oracle.acquire()
        cursor = conexao.cursor()

        # O MESTRE DOS JOINS: Conecta 4 tabelas relacionais de uma vez!
        comando_sql = """
            SELECT 
                c.DATA_COTACAO, 
                c.PRECO_COMPRA, 
                s.VALOR_TAXA, 
                f.VALOR_EXPECTATIVA 
            FROM TB_COTACAO c 
            JOIN TB_MOEDA m ON c.ID_MOEDA = m.ID_MOEDA
            LEFT JOIN TB_TAXA_SELIC s ON c.DATA_COTACAO = s.DATA_TAXA 
            LEFT JOIN TB_BOLETIM_FOCUS f ON c.DATA_COTACAO = f.DATA_REFERENCIA
            WHERE m.NOME_MOEDA = :1
            ORDER BY c.DATA_COTACAO ASC
        """
        cursor.execute(comando_sql, [nome_moeda])
        return cursor.fetchall()

    except Exception as erro:
        st.error(f"Falha na integração de dados. Erro: {erro}")
        return []
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexao' in locals(): pool_oracle.release(conexao)


# --- 3. EXIBIÇÃO DE DADOS (FRONTEND SIMPLIFICADO) ---
# Injeta a moeda selecionada na busca
dados_macro = buscar_dados_macro(moeda_selecionada)

if dados_macro:
    # Ajusta o nome da coluna dinamicamente para Dólar ou Euro
    coluna_moeda = f"{moeda_selecionada} (Compra)"
    
    df_macro = pd.DataFrame(
        dados_macro, 
        columns=["Data", coluna_moeda, "Meta Selic", "Expectativa Focus"]
    )
    df_macro["Data"] = pd.to_datetime(df_macro["Data"])
    df_macro.set_index("Data", inplace=True)
    df_macro = df_macro.ffill()

    # Agrupa os dados por mês
    df_mensal = df_macro.resample('ME').mean()

    # TOPO: Cartões de Métricas
    st.write("### Panorama Atual")
    
    ultima_linha = df_macro.iloc[-1] 
    
    col1, col2, col3 = st.columns(3)
    col1.metric(moeda_selecionada, f"R$ {ultima_linha[coluna_moeda]:.2f}")
    col2.metric("Selic", f"{ultima_linha['Meta Selic']:.2f}%")
    col3.metric("Focus", f"{ultima_linha['Expectativa Focus']:.2f}%")

    st.markdown("---")

    # MEIO: O Gráfico Nativo
    st.write(f"### Tendência Histórica: {moeda_selecionada} vs Selic vs Expectativas")
    st.line_chart(df_mensal[[coluna_moeda, "Meta Selic", "Expectativa Focus"]])

    # FIM: Tabela Escondida
    with st.expander("Ver Base de Dados Completa"):
        st.dataframe(df_macro, use_container_width=True)

else:
    st.warning("Aviso: Nenhum dado foi encontrado no banco de dados para os parâmetros selecionados.")