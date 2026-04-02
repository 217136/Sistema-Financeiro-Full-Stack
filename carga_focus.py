import os
import oracledb
import pandas as pd  # Adicionado para manipulação segura das datas
from dotenv import load_dotenv
from bcb import Expectativas

# --- 1. EXTRAÇÃO ---
print("Extraindo dados do Boletim Focus (Selic para 2026)...")
expec = Expectativas()
ep = expec.get_endpoint('ExpectativasMercadoAnuais')

# Executando a consulta e filtrando por Selic
dados_esperados = ep.query().filter(ep.Indicador == 'Selic').collect()

# --- 2. TRANSFORMAÇÃO ---
# Filtrando as expectativas apenas para o ano de 2026
df_filtrado = dados_esperados[dados_esperados['DataReferencia'] == '2026']

# 🚨 O ESCUDO ANTI-DUPLICIDADE: Garante apenas uma projeção por dia!
df_unico = df_filtrado.drop_duplicates(subset=['Data'], keep='last')

# Convertendo para a Matriz de Tuplas formatada para o Oracle
matriz_focus = []
for linha in df_unico[['Data', 'Mediana']].values:
    # Garante que a data vá como texto 'YYYY-MM-DD' e o valor como float
    data_formatada = pd.to_datetime(linha[0]).strftime('%Y-%m-%d')
    valor = float(linha[1])
    matriz_focus.append((data_formatada, valor))


# --- 3. CARGA SEGURA NO BANCO DE DADOS (LOAD) ---
print(f"Iniciando a injeção segura de {len(matriz_focus)} registros no Oracle Cloud...")
load_dotenv()

try:
    conexao = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        dsn=os.getenv("DB_DSN")
    )
    cursor = conexao.cursor()

    # 🚨 HIGIENE DE CARGA: Limpa os dados antigos antes de inserir os novos
    # Isso impede o erro ORA-00001 caso você rode o script mais de uma vez
    cursor.execute("TRUNCATE TABLE TB_BOLETIM_FOCUS")

    # Instrução SQL parametrizada com TO_DATE para evitar conflito de tipos
    comando_insercao = """
        INSERT INTO TB_BOLETIM_FOCUS (DATA_REFERENCIA, VALOR_EXPECTATIVA) 
        VALUES (TO_DATE(:1, 'YYYY-MM-DD'), :2)
    """

    # Execução massiva da matriz no banco de dados
    cursor.executemany(comando_insercao, matriz_focus)
    conexao.commit()

    print(f"🚀 Sucesso! {cursor.rowcount} registros únicos do Focus foram inseridos no banco de dados!")

except Exception as erro:
    print("Falha na operação de carga. Erro:", erro)
    
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conexao' in locals():
        conexao.close()