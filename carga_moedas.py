import os
import oracledb
import pandas as pd
import random
from dotenv import load_dotenv
from bcb import PTAX 

print("Iniciando extração múltipla: Dólar e Euro via API OData (PTAX)...")
ptax = PTAX()

# Dicionário de controle: Símbolo na API -> ID_MOEDA no banco de dados
moedas_alvo = {
    'USD': 1, # ID 1 = Dólar
    'EUR': 2  # ID 2 = Euro
}

matriz_cotacoes = []

# Loop que processa cada moeda e atrela ao seu ID
for simbolo, id_moeda in moedas_alvo.items():
    print(f"Buscando cotações para: {simbolo} (ID: {id_moeda})")
    
    # O Banco Central tem endpoints levemente diferentes para Dólar e outras moedas
    if simbolo == 'USD':
        ep = ptax.get_endpoint('CotacaoDolarPeriodo')
        df_moeda = ep.query().parameters(dataInicial='01-01-2024', dataFinalCotacao='03-22-2026').collect()
    else:
        ep = ptax.get_endpoint('CotacaoMoedaPeriodo')
        df_moeda = ep.query().parameters(moeda=simbolo, dataInicial='01-01-2024', dataFinalCotacao='03-22-2026').collect()

    df_final = df_moeda[['dataHoraCotacao', 'cotacaoCompra', 'cotacaoVenda']]

    # 1. Fazemos uma cópia limpa das 3 colunas
    df_final = df_moeda[['dataHoraCotacao', 'cotacaoCompra', 'cotacaoVenda']].copy()
    
    # 2. Padronizamos toda a coluna de DataHora para apenas Data (YYYY-MM-DD)
    df_final['dataHoraCotacao'] = pd.to_datetime(df_final['dataHoraCotacao']).dt.strftime('%Y-%m-%d')
    
    # 3. A MÁGICA: Removemos os dias duplicados, mantendo sempre a última cotação (fechamento)
    df_final = df_final.drop_duplicates(subset=['dataHoraCotacao'], keep='last')

    # 4. Agora sim, montamos a matriz com a certeza de que há apenas 1 dia para cada moeda
    for linha in df_final.values:
        data_nativa = linha[0]  # Já está formatado como string  
        compra_nativa = float(linha[1])    
        venda_nativa = float(linha[2])     
        volume = random.uniform(1000000.0, 50000000.0) 
        
        matriz_cotacoes.append((data_nativa, id_moeda, compra_nativa, venda_nativa, volume))

print(f"Iniciando injeção de {len(matriz_cotacoes)} registros na TB_COTACAO...")
load_dotenv()

try:
    conexao = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        dsn=os.getenv("DB_DSN")
    )
    cursor = conexao.cursor()

    # Limpa a tabela antes da carga total
    cursor.execute("TRUNCATE TABLE TB_COTACAO")

    # O INSERT agora aponta para a nova estrutura normalizada
    comando_insercao = """
        INSERT INTO TB_COTACAO (DATA_COTACAO, ID_MOEDA, PRECO_COMPRA, PRECO_VENDA, VOLUME)
        VALUES (TO_DATE(:1, 'YYYY-MM-DD'), :2, :3, :4, :5)
    """
    
    cursor.executemany(comando_insercao, matriz_cotacoes)
    conexao.commit()

    print(f"🚀 Sucesso Absoluto! {cursor.rowcount} registros consolidados foram inseridos!")

except Exception as erro:
    print("Falha na operação de carga. Erro:", erro)
finally:
    if 'cursor' in locals(): cursor.close()
    if 'conexao' in locals(): 
        conexao.close()
        print("Conexão encerrada com segurança.")