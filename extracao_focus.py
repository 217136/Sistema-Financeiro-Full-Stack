# 1. Importação da classe Expectativas
from bcb import Expectativas

# 2. Instanciando a classe e definindo o endpoint de expectativas anuais
expec = Expectativas()
ep = expec.get_endpoint('ExpectativasMercadoAnuais')

# 3. Executando a consulta e filtrando por um indicador genérico
dados_esperados = ep.query().filter(ep.Indicador == 'Selic').collect()

print(dados_esperados)