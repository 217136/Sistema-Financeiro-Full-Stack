# 📊 Sistema Financeiro Full-Stack

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sistema-financeiro-full-stack-sh6ncmvfwzwmdguworjasw.streamlit.app/)

Este projeto é uma aplicação analítica de ponta a ponta desenvolvida para monitoramento macroeconômico, unindo extração de dados automatizada (ETL), modelagem de banco de dados relacional em nuvem e visualização interativa.

## 🏛️ Arquitetura do Projeto

O sistema foi construído sob uma arquitetura modular, separando responsabilidades de infraestrutura, engenharia de dados e frontend:

1. **Banco de Dados (Oracle Cloud Free Tier):** Modelagem física normalizada e blindada com Chaves Primárias (PK) e Estrangeiras (FK).
2. **Engenharia de Dados (ETL em Python):** Scripts independentes que consomem a API OData do Banco Central do Brasil (SGS e PTAX), aplicam higienização de dados (remoção de duplicatas e rotinas de `TRUNCATE`) e realizam inserção massiva (`executemany`) no banco.
3. **Frontend (Streamlit):** Dashboards interativos para a renderização de métricas institucionais (TWAP/VWAP) e gráficos macroeconômicos de volatilidade.

## 🔒 Segurança e Governança

O projeto utiliza **Conexão Oracle via TLS (Walletless)**, dispensando o uso de arquivos físicos (Wallets) para autenticação. Todas as credenciais de banco de dados são injetadas de forma segura em tempo de execução através de variáveis de ambiente (`.env`), impedindo o vazamento de dados sensíveis no código-fonte.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Banco de Dados:** Oracle SQL (Cloud)
* **Bibliotecas de Dados:** Pandas, python-bcb
* **Visualização:** Streamlit, Plotly
* **Segurança e Conexão:** oracledb (Thin mode), python-dotenv

## 🗂️ Estrutura de Arquivos e Banco de Dados

O ecossistema utiliza tabelas relacionais para garantir integridade e performance. A fundação estrutural está documentada em:

* `modelagem_fisica.sql`: Script DDL contendo a criação das tabelas blindadas.
    * `TB_MOEDA`: Tabela de domínio (Dólar, Euro).
    * `TB_COTACAO`: Tabela fato normalizada contendo histórico diário e volumes.
    * `TB_TAXA_SELIC`: Histórico da meta de juros do Copom.
    * `TB_BOLETIM_FOCUS`: Projeções de mercado.
* `carga_selic.py` / `carga_focus.py` / `carga_moedas.py`: Robôs independentes de extração e carga.
* `/pages/`: Diretório contendo os módulos analíticos do Frontend (Câmbio e Macroeconomia).

## 🚀 Como Executar Localmente

1. Clone este repositório.
2. Crie um arquivo `.env` na raiz do projeto com as suas credenciais do Oracle Cloud (`DB_USER`, `DB_PASS`, `DB_DSN`).
3. Instale as dependências executando: `pip install -r requirements.txt`.
4. Crie as tabelas rodando o conteúdo de `modelagem_fisica.sql` no seu banco de dados.
5. Execute os scripts de carga (`carga_moedas.py`, `carga_selic.py`, `carga_focus.py`) para popular seu banco com dados atualizados.
6. Inicie a aplicação web com o comando: `streamlit run frontend.py`.