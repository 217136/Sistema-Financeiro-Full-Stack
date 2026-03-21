import os
import oracledb
from dotenv import load_dotenv

# 1. Carrega as credenciais seguras do cofre .env
load_dotenv()

try:
    # 2. Estabelece a conexão no modo Thin com o Oracle FreeSQL Cloud
    conexao = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        dsn=os.getenv("DB_DSN")
    )
    cursor = conexao.cursor()

    # 3. O comando SQL de criação de tabela que você modelou
    comando_criacao = """
        CREATE TABLE TB_BOLETIM_FOCUS (
            DATA_REFERENCIA DATE,
            VALOR_EXPECTATIVA FLOAT
        )
    """

    # 4. Executando o comando estrutural na nuvem
    print("Enviando ordem de criação de tabela para o Oracle Cloud...")
    cursor.execute(comando_criacao)
    
    print("Sucesso! A tabela TB_BOLETIM_FOCUS foi construída na nuvem!")

    # 5. Higiene Digital
    cursor.close()
    conexao.close()

except Exception as erro:
    print("Falha ao criar a tabela. Erro:", erro)