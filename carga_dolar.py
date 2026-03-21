import os
import oracledb
import pandas as pd
from dotenv import load_dotenv
from bcb import currency

# --- 1. EXTRAÇÃO E TRANSFORMAÇÃO (ETL) ---
print("Extraindo histórico de Cotação do Dólar via API do Banco Central...")

# A extração retorna um DataFrame com o Índice (Data) e uma coluna ('USD')
df_dolar = currency.get(['USD'], start='2026-01-01', end='2026-03-19')
df_dolar = df_dolar.reset_index()

# TRANSFORMANDO OS DADOS (O "T" do ETL)
# O banco exige 3 colunas. Vamos duplicar o valor do Dólar para Compra e Venda
df_dolar['PRECO_COMPRA'] = df_dolar['USD']
df_dolar['PRECO_VENDA'] = df_dolar['USD']

# Filtrando e ordenando estritamente as 3 colunas que o Oracle espera
df_final = df_dolar[['Date', 'PRECO_COMPRA', 'PRECO_VENDA']]

# Agora a Matriz de Tuplas terá exatamente 3 valores alinhados por linha!
matriz_dolar = [tuple(linha) for linha in df_final.values]


# --- 2. CARGA SEGURA NO BANCO DE DADOS (LOAD) ---
print("Iniciando injeção segura de dados na TB_COTACAO_DOLAR...")
load_dotenv()

try:
    conexao = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        dsn=os.getenv("DB_DSN")
    )
    cursor = conexao.cursor()

    # O Comando SQL com exatas 3 Variáveis de Ligação Protegidas
    comando_insercao = """
        INSERT INTO TB_COTACAO_DOLAR (DATA_COTACAO, PRECO_COMPRA, PRECO_VENDA) 
        VALUES (:1, :2, :3)
    """

    # Injeção em massa e gravação da transação
    cursor.executemany(comando_insercao, matriz_dolar)
    conexao.commit()

    print(f"Sucesso! {cursor.rowcount} registros do Dólar foram inseridos!")

    # Higiene Digital
    cursor.close()
    conexao.close()

except Exception as erro:
    print("Falha na operação de carga. Erro:", erro)