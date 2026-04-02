import streamlit as st

# 1. Configuração da Página (Aba do Navegador)
st.set_page_config(
    page_title="Sistema Financeiro Full-Stack",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Cabeçalho Principal
st.title("🏦 Sistema Financeiro Full-Stack")
st.subheader("Plataforma Analítica de Indicadores Macroeconômicos")
st.markdown("---")

# 3. Contextualização do Projeto
col1, col2 = st.columns([2, .75])

with col1:
    st.markdown("""
    ### Bem-vindo ao Painel de Controle
    
    Este sistema foi desenvolvido como uma aplicação de ponta a ponta, aplicando conceitos avançados de **Engenharia de Dados** e **Modelagem Relacional**. O objetivo é monitorar e cruzar os principais indicadores da economia brasileira com base em fontes oficiais.
    
    ### 🎯 Navegação (Menu Lateral)
        
    * **1️⃣ Moedas, TWAP e VWAP:** Análise diária da volatilidade de moedas estrangeiras (Dólar e Euro), incluindo o cálculo de métricas de execução institucional (TWAP e VWAP).
    * **2️⃣ Macroeconomia Integrada:** Um cruzamento relacional que demonstra na prática o efeito "gangorra" entre o Câmbio, a Taxa Selic e as Expectativas do Mercado (Boletim Focus).
    """)

with col2:
    st.info("""
    **⚙️ Arquitetura sob o Capô:**
    
    * **Banco de Dados:** Oracle Cloud Free Tier
    * **Modelagem:** Entidade-Relacionamento (Normalizada)
    * **Pipelines ETL:** Python (Extração automatizada da API OData do BCB)
    * **Frontend:** Streamlit & Plotly
    """)

st.markdown("---")

# 4. Rodapé Informativo
st.markdown("""
> 💡 **Dica de Uso:** Todos os gráficos são interativos. Você pode dar zoom, isolar variáveis e passar o mouse sobre as linhas para ver os valores exatos de cada dia. A aplicação consome dados diretamente da nuvem em tempo real através de um Pool de Conexões protegido.
""")