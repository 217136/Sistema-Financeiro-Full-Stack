import os
import oracledb
from dotenv import load_dotenv
from bcb import sgs

# --- 1. EXTRAÇÃO E TRANSFORMAÇÃO (ETL) ---
print("Extraindo dados da Meta Selic do Banco Central...")
# Acessando o código identificador 432 da Meta Selic via API SGS
dados_juros = sgs.get({'Selic': 432}, start='2024-01-01')

# Trazendo a Data, que vem como índice, para uma coluna normal
dados_juros = dados_juros.reset_index()

# Transformando o DataFrame do Pandas na Matriz de Tuplas exigida pelo Oracle
matriz_selic = [tuple(linha) for linha in dados_juros.values]


# --- 2. CARGA SEGURA NO BANCO DE DADOS (LOAD) ---
print("Iniciando a injeção segura de dados no Oracle Cloud...")
load_dotenv()

try:
    conexao = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        dsn=os.getenv("DB_DSN")
    )
    cursor = conexao.cursor()

    # Instrução SQL parametrizada com Variáveis de Ligação (Bind Variables)
    comando_insercao = """
        INSERT INTO TB_TAXA_SELIC (DATA_REFERENCIA, VALOR_META_SELIC) 
        VALUES (:1, :2)
    """

    # Execução massiva da matriz no banco de dados
    cursor.executemany(comando_insercao, matriz_selic)
    
    # Transação obrigatória para salvar as linhas fisicamente na nuvem
    conexao.commit()

    print(f"Sucesso! {cursor.rowcount} registros da Selic foram inseridos no banco de dados!")

    # Higiene Digital
    cursor.close()
    conexao.close()

except Exception as erro:
    print("Falha na operação de carga. Erro:", erro)