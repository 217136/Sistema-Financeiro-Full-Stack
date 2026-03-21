import os
import oracledb
from dotenv import load_dotenv
from bcb import PTAX

# --- 1. EXTRAÇÃO E TRANSFORMAÇÃO ---
print("Conectando à API OData do Banco Central...")
ptax = PTAX()
ep = ptax.get_endpoint('CotacaoDolarPeriodo')

# Injetando as datas no padrão americano exigido pela API
df_dolar = ep.query().parameters(dataInicial='01-01-2024', dataFinalCotacao='01-10-2024').collect()
df_filtrado = df_dolar[['dataHoraCotacao', 'cotacaoCompra', 'cotacaoVenda']]

# Transformação do DataFrame em Matriz (Lista de Tuplas) para o banco de dados
matriz_de_dados = [tuple(linha) for linha in df_filtrado.values]

# --- 2. CARGA SEGURA NO BANCO (LOAD) ---
print("Iniciando a carga de dados no Oracle Cloud...")
load_dotenv()

try:
    conexao = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        dsn=os.getenv("DB_DSN")
    )
    cursor = conexao.cursor()

    comando_sql = """
        INSERT INTO TB_COTACAO_DOLAR (DATA_COTACAO, PRECO_COMPRA, PRECO_VENDA) 
        VALUES (:1, :2, :3)
    """

    cursor.executemany(comando_sql, matriz_de_dados)
    conexao.commit()
    
    print(f"Sucesso! {cursor.rowcount} linhas inseridas no banco de dados!")

    # Higiene Digital
    cursor.close()
    conexao.close()
    
except Exception as erro:
    print("Falha no processo de ETL. Erro:", erro)