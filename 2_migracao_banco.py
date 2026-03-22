import os
import oracledb
from dotenv import load_dotenv

def executar_migracao():
    # 1. Carrega as variáveis de ambiente protegidas no arquivo .env
    load_dotenv()
    
    conexao = None
    try:
        # 2. Estabelece a conexão Thin com o Oracle Cloud de forma segura
        conexao = oracledb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            dsn=os.getenv("DB_DSN")
        )
        cursor = conexao.cursor()
        
        print("Conexão estabelecida. Iniciando alteração no banco de dados...")
        
        # 3. Definição do Comando DDL Genérico (Substitua pela sua instrução real)
        comando_ddl = """
            ALTER TABLE TB_COTACAO_DOLAR ADD VOLUME NUMBER
        """
        
        # 4. Execução do Comando
        cursor.execute(comando_ddl)
        print("Sucesso: Comando DDL executado. A estrutura da tabela foi alterada!")
        
        # Opcional: Você pode colocar múltiplos cursor.execute() aqui se tiver 
        # outras tabelas para alterar no futuro.

    except Exception as erro:
        print(f"Falha ao alterar o banco de dados. Erro: {erro}")
        
    finally:
        # 5. Higiene Digital: Garantir o fechamento do cursor e da conexão
        if 'cursor' in locals():
            cursor.close()
        if conexao is not None:
            conexao.close()
            print("Conexão encerrada com segurança.")

# Ponto de entrada do script
if __name__ == "__main__":
    executar_migracao()