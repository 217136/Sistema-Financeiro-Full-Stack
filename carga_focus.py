# 1. Importação da classe Expectativas
from bcb import Expectativas

# 2. Instanciando a classe e definindo o endpoint de expectativas anuais
expec = Expectativas()
ep = expec.get_endpoint('ExpectativasMercadoAnuais')

# 3. Executando a consulta e filtrando por um indicador genérico
dados_esperados = ep.query().filter(ep.Indicador == 'Selic').collect()

print(dados_esperados)

# 4. Transformação: Filtrando as expectativas apenas para o ano de 2026
df_filtrado = dados_esperados[dados_esperados['DataReferencia'] == '2026']

# 5. Isolando as duas colunas que correspondem à nossa modelagem do Banco de Dados
df_final = df_filtrado[['Data', 'Mediana']]

# 6. Convertendo para a Matriz de Tuplas para o Oracle
matriz_focus = [tuple(linha) for linha in df_final.values]

import os
import oracledb
from dotenv import load_dotenv

# 7. CARGA SEGURA NO BANCO DE DADOS (LOAD)
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
        INSERT INTO TB_BOLETIM_FOCUS (DATA_REFERENCIA, VALOR_EXPECTATIVA) VALUES (:1, :2)
    """

    # Execução massiva da matriz no banco de dados
    cursor.executemany(comando_insercao, matriz_focus)
    
    # Transação obrigatória para salvar as linhas fisicamente na nuvem
    conexao.commit()

    print(f"Sucesso! {cursor.rowcount} registros da Focus foram inseridos no banco de dados!")

    # Higiene Digital
    cursor.close()
    conexao.close()

except Exception as erro:
    print("Falha na operação de carga. Erro:", erro)