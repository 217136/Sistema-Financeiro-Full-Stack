import os
import oracledb
import pandas as pd
import random
from dotenv import load_dotenv
from bcb import PTAX 

# --- 1. EXTRAÇÃO E TRANSFORMAÇÃO (ETL) MULTI-MOEDAS ---
print("Iniciando extração múltipla: Dólar e Euro via API OData (PTAX)...")
ptax = PTAX()

# Dicionário de controle: Símbolo na API -> ID_MOEDA no nosso Oracle Cloud
moedas_alvo = {
    'USD': 1, # ID 1 = Dólar
    'EUR': 2  # ID 2 = Euro
}

matriz_cotacoes = []

# O Loop Mágico: Roda uma vez para o Dólar, depois roda para o Euro
for simbolo, id_moeda in moedas_alvo.items():
    print(f"Buscando cotações e processando dados para: {simbolo} (ID: {id_moeda})")
    
    # O Banco Central tem endpoints levemente diferentes para Dólar e outras moedas
    if simbolo == 'USD':
        ep = ptax.get_endpoint('CotacaoDolarPeriodo')
        df_moeda = ep.query().parameters(dataInicial='01-01-2024', dataFinalCotacao='03-21-2026').collect()
    else:
        ep = ptax.get_endpoint('CotacaoMoedaPeriodo')
        df_moeda = ep.query().parameters(moedaCotacao=simbolo, dataInicial='01-01-2024', dataFinalCotacao='03-21-2026').collect()

    # Isolamos as colunas padronizadas retornadas pela API
    df_final = df_moeda[['dataHoraCotacao', 'cotacaoCompra', 'cotacaoVenda']]

    # Construção da Matriz unificada
    for linha in df_final.values:
        data_nativa = pd.to_datetime(linha[0]).strftime('%Y-%m-%d')   
        compra_nativa = float(linha[1])    
        venda_nativa = float(linha[2])     
        volume = random.uniform(1000000.0, 50000000.0) 
        
        # 🚨 A GRANDE MUDANÇA: Agora injetamos o 'id_moeda' na tupla!
        matriz_cotacoes.append((data_nativa, id_moeda, compra_nativa, venda_nativa, volume))


# --- 2. CARGA SEGURA NO BANCO DE DADOS (LOAD) ---
print(f"Iniciando injeção segura de {len(matriz_cotacoes)} registros totais na TB_COTACAO...")
load_dotenv()

try:
    conexao = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        dsn=os.getenv("DB_DSN")
    )
    cursor = conexao.cursor()

    # Limpa a NOVA tabela fato normalizada
    cursor.execute("TRUNCATE TABLE TB_COTACAO")

    # O INSERT agora aponta para a nova estrutura e exige 5 parâmetros (incluindo o ID_MOEDA)
    comando_insercao = """
        INSERT INTO TB_COTACAO (DATA_COTACAO, ID_MOEDA, PRECO_COMPRA, PRECO_VENDA, VOLUME)
        VALUES (TO_DATE(:1, 'YYYY-MM-DD'), :2, :3, :4, :5)
    """
    
    # Um único executemany salva anos de dados do Dólar e do Euro em milissegundos
    cursor.executemany(comando_insercao, matriz_cotacoes)
    conexao.commit()

    print(f"Sucesso Absoluto! {cursor.rowcount} registros consolidados foram inseridos!")

except Exception as erro:
    print("Falha na operação de carga. Erro:", erro)
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conexao' in locals():
        conexao.close()
        print("Conexão com o Oracle encerrada com segurança.")