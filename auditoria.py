import os
import oracledb
from dotenv import load_dotenv

# Telemetria 1
print("1. Carregando variáveis de ambiente...")
load_dotenv()

try:
    # Telemetria 2
    print("2. Tentando conectar ao Oracle Cloud (Aguarde)...")
    conexao = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        dsn=os.getenv("DB_DSN")
    )
    
    # Telemetria 3
    print("3. Conexão bem-sucedida! Executando a consulta...")
    cursor = conexao.cursor()
    
    comando_sql = "SELECT COUNT(*) FROM TB_COTACAO_DOLAR"
    cursor.execute(comando_sql)
    
    # Desempacotando a tupla retornada pelo COUNT
    quantidade_linhas, = cursor.fetchone()
    
    print(f"4. Sucesso! A tabela do Dólar possui {quantidade_linhas} registros.")

    # Higiene Digital Absoluta [1]
    cursor.close()
    conexao.close()
    print("5. Conexão encerrada com segurança.")

except Exception as erro:
    print(f"FALHA CRÍTICA DETECTADA: {erro}")