# Resumo Executivo: Sistema Financeiro Full Stack 🏦

Este documento destrincha a arquitetura do projeto de forma didática e transparente, alinhando a visão de negócios com a Engenharia de Software e o Banco de Dados Relacional. O objetivo é nivelar o conhecimento entre todos os *stakeholders* (partes interessadas).

---

## 🏛️ Parte 1: O Passo a Passo do Desenvolvimento

A construção do sistema seguiu uma ordem lógica de fundação, encanamento e acabamento:

1. **A Fundação (Banco de Dados na Nuvem):** Em vez de usar planilhas, decidimos construir a base do sistema em um banco de dados corporativo real, o **Oracle Cloud** (*Free Tier*). Isso garantiu armazenamento seguro, alta disponibilidade e acesso remoto.
2. **A Modelagem (As Tabelas):** Desenhamos quatro estruturas conectadas:
   * `TB_MOEDA`: Cadastro das moedas (Dólar, Euro).
   * `TB_COTACAO`: Valor diário de compra e venda.
   * `TB_TAXA_SELIC`: Histórico da taxa básica de juros.
   * `TB_BOLETIM_FOCUS`: Expectativas do mercado financeiro.
3. **O Encanamento (Pipeline ETL):** Construímos robôs em Python que consomem a API pública do Banco Central do Brasil, extraem os dados brutos, limpam as inconsistências e injetam esses dados de forma organizada no Oracle.
4. **O Acabamento (Frontend no Streamlit):** Criamos o painel visual. Ele se conecta ao banco de dados, realiza cálculos matemáticos complexos e desenha os gráficos. Tudo foi publicado na internet automatizando o processo via GitHub (CI/CD).

---

## ⚙️ Parte 2: A Engenharia de Dados (ETL)

O coração do sistema é o processo de **ETL (Extract, Transform, Load)**:

* **Extração:** Consulta direta e automatizada ao "SGS" e à "PTAX" (fontes oficiais do Governo Federal).
* **Tratamento:** A internet possui "dados sujos". O Banco Central, por vezes, envia múltiplas leituras diárias. Para não quebrar o banco, usamos a biblioteca *Pandas* para analisar os dados em memória, apagando duplicatas e garantindo a entrada apenas do valor oficial de fechamento.
* **Carga (Alta Performance):** Empacotamos milhares de linhas e enviamos para o Oracle em lote (técnica `executemany`), otimizando o tráfego de rede e o tempo de processamento.

---

## 🧮 Parte 3: As Funcionalidades e Cálculos

O painel gera **inteligência financeira** baseada em dados:

* **Cálculo de VWAP e TWAP:** O sistema calcula o *Preço Médio Ponderado pelo Volume* (VWAP) e o *Preço Médio Ponderado pelo Tempo* (TWAP), métricas institucionais usadas para definir o preço justo de um ativo, ignorando a histeria momentânea do mercado.
* **Módulo de Câmbio:** Mostra a volatilidade diária. Como a API não fornece volume real (dado pago e restrito na B3), injetamos um "volume sintético" estritamente para homologar o motor de cálculo do banco de dados.
* **Módulo de Macroeconomia:** Cruza Câmbio, Selic e Boletim Focus, permitindo visualizar na prática a "gangorra" da economia brasileira.

---

## 🧠 Parte 4: Decisões Arquiteturais (O Porquê)

1. **Por que Oracle e não NoSQL?** Dados financeiros exigem regras estritas (*Constraints*). Quando um dado duplicado tenta entrar, o banco gera o erro `ORA-00001` e barra a operação, provando que a segurança relacional funciona.
2. **Por que esconder senhas no Streamlit Secrets?** O código é aberto (Open Source), mas credenciais de banco não podem ser expostas. Criamos um "cofre" virtual na nuvem, aplicando conceitos de *DevSecOps*.
3. **Por que o volume simulado?** Para focar na arquitetura e manter o custo do projeto em R$ 0,00 (*Cost Avoidance*). O volume sintético homologa perfeitamente as funções de agregação (SUM, AVG) exigidas pelo laboratório de Banco de Dados.
4. **Eficiência em Manutenção de Segurança:** Em abril de 2026, o sistema passou por uma migração crítica de protocolos de segurança (de mTLS para TLS) devido à expiração global de certificados G1. Graças à arquitetura baseada em variáveis de ambiente (.env e Streamlit Secrets), a transição foi realizada com zero alteração de código, garantindo a continuidade do serviço e a integridade da conexão com o Oracle Cloud de forma transparente e segura.

---

## 📈 Parte 5: Usabilidade e Mercado Consumidor

**Público-alvo para esta arquitetura no mundo real:**
* **Tesourarias Corporativas:** Empresas de importação/exportação que utilizam o VWAP para auditar se estão pagando um preço justo nas operações de câmbio.
* **Fundos de Investimento:** Gestores que cruzam inflação (Focus) e juros (Selic) para decidir alocação de capital.
* **Controladoria e Auditoria:** Sistemas baseados em banco de dados relacional imutável servem como "fonte da verdade" auditável para balanços.