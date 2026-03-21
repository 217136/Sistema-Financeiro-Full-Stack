import os
import oracledb
from dotenv import load_dotenv

# 1. SEGURANÇA: Carregando as credenciais do seu cofre digital
load_dotenv()

try:
    # 2. CONEXÃO: Estabelecendo a ponte com o Oracle Cloud FreeSQL
    conexao = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        dsn=os.getenv("DB_DSN")
    )
    cursor = conexao.cursor()

    # 3. LÓGICA DE PROCESSAMENTO (SQL): Cálculo do TWAP Diário
    comando_sql = """
        SELECT 
            AVG(PRECO_COMPRA) AS MEDIA_COMPRA, 
            AVG(PRECO_VENDA) AS MEDIA_VENDA 
        FROM TB_COTACAO_DOLAR
    """

    # 4. EXECUÇÃO E EXTRAÇÃO (Com Desempacotamento)
    print("Enviando ordem de cálculo para o Oracle Cloud...")
    cursor.execute(comando_sql)

    # O método fetchone() retorna a tupla. 
    # Nós a desempacotamos diretamente em duas variáveis numéricas isoladas!
    media_compra, media_venda = cursor.fetchone()

    # 5. APRESENTAÇÃO
    print(f"\nSucesso! TWAP Calculado pelo motor do Banco de Dados:")
    print(f"Média Ponderada de Compra (TWAP): R$ {media_compra:.4f}")
    print(f"Média Ponderada de Venda (TWAP): R$ {media_venda:.4f}")

    # 6. HIGIENE DIGITAL: Fechar os recursos 
    cursor.close()
    conexao.close()

except Exception as erro:
    print("Falha na operação de cálculo. Erro:", erro)