# Sistema-Financeiro-Full-Stack
O projeto desenvolvido é um Sistema Financeiro Full-Stack de Análise Macroeconômica, projetado sob rigorosos padrões de Engenharia de Software e Banco de Dados. A sua arquitetura validada e estruturada divide-se nas seguintes camadas técnicas fundamentais:
Fonte de Dados (Extração): O sistema consome informações em tempo real da API de Dados Abertos do Banco Central do Brasil
. A extração é realizada via Python utilizando a biblioteca python-bcb, que acessa o Sistema Gerenciador de Séries Temporais (SGS) para a Taxa Selic, o endpoint de Expectativas para o Boletim FOCUS e o módulo de moedas (PTAX) para a cotação comercial de compra e venda do Dólar
.
Banco de Dados e Segurança (Armazenamento): Toda a persistência de dados ocorre em um banco de dados relacional em nuvem, o Oracle FreeSQL Cloud
. A comunicação backend opera através da biblioteca python-oracledb no modo Thin, e a infraestrutura obedece aos mais altos padrões de Higiene Digital e Segurança da Informação: as credenciais do banco nunca são expostas no código-fonte, sendo estritamente geridas por variáveis de ambiente em um arquivo .env através da biblioteca python-dotenv
.
Motor Relacional (Transformação e Lógica): A modelagem dos dados baseia-se em tabelas de domínio isoladas para cada indicador (TB_COTACAO_DOLAR, TB_TAXA_SELIC e TB_BOLETIM_FOCUS)
. O sistema delega o processamento pesado de cruzamento de dados e cálculo de indicadores matemáticos (como o TWAP) diretamente para o motor do Oracle, utilizando instruções SQL complexas com múltiplos INNER JOIN e funções agregadas como AVG() e COUNT()
.
Frontend (Apresentação e Interatividade): A camada visual é um Dashboard web multipágina, de roteamento inteligente, construído inteiramente em Python com o framework Streamlit
. A interface aplica as melhores práticas de UI/UX, exibindo métricas de fácil leitura e gráficos de linha recomendados para séries temporais (sem distorções visuais)
.
[Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sistema-financeiro-full-stack-sh6ncmvfwzwmdguworjasw.streamlit.app)

. Para garantir alta performance de rede e prevenir gargalos no banco de dados, o sistema faz uso avançado do gerenciamento de cache em memória RAM através do decorador @st.cache_data
