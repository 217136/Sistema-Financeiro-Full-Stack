# 📊 Sistema Financeiro Full-Stack

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)(https://sistema-financeiro-full-stack-sh6ncmvfwzwmdguworjasw.streamlit.app/)]

Este projeto é uma aplicação analítica de ponta a ponta desenvolvida para monitoramento macroeconômico, unindo extração de dados automatizada (ETL), modelagem de banco de dados relacional em nuvem e visualização interativa.

## 🏛️ Arquitetura do Projeto

O sistema foi construído sob uma arquitetura modular, separando responsabilidades de infraestrutura, engenharia de dados e frontend:

1. **Banco de Dados (Oracle Cloud Free Tier):** Modelagem normalizada com chaves primárias e estrangeiras, preparada para receber múltiplas moedas de forma escalável.
2. **Engenharia de Dados (ETL em Python):** Scripts independentes que consomem a API OData do Banco Central do Brasil (SGS e PTAX), aplicam regras de negócio (como deduplicação e cálculo de volume simulado) e realizam inserção massiva (`executemany`) no banco de dados.
3. **Frontend (Streamlit):** Dashboards interativos e cacheados, garantindo alta performance na renderização de métricas (TWAP/VWAP) e gráficos de volatilidade.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Banco de Dados:** Oracle SQL (Cloud)
* **Bibliotecas de Dados:** Pandas, python-bcb
* **Visualização:** Streamlit, Plotly
* **Segurança e Conexão:** oracledb, python-dotenv (Variáveis de Ambiente)

## 🗂️ Estrutura de Banco de Dados

O ecossistema utiliza tabelas relacionais para garantir integridade e performance:
* `TB_MOEDA`: Tabela de domínio (Dólar, Euro).
* `TB_COTACAO`: Tabela fato normalizada contendo histórico diário e volumes.
* `TB_TAXA_SELIC`: Histórico da meta de juros do Copom.
* `TB_BOLETIM_FOCUS`: Projeções de mercado.

## 🚀 Como Executar Localmente

1. Clone este repositório.
2. Crie um arquivo `.env` na raiz do projeto com as suas credenciais do Oracle Cloud (`DB_USER`, `DB_PASS`, `DB_DSN`).
3. Instale as dependências executando: `pip install -r requirements.txt`.
4. (Opcional) Execute os scripts de carga (`carga_moedas.py`, `carga_selic.py`) para popular seu banco.
5. Inicie a aplicação web com o comando: `streamlit run frontend.py`.