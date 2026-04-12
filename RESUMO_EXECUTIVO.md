Resumo Executivo: Sistema Financeiro Full Stack 🏦

Este documento destrincha a arquitetura do projeto de forma didática e transparente, alinhando a visão de negócios com a Engenharia de Software e o Banco de Dados Relacional. O objetivo é nivelar o conhecimento entre todos os stakeholders (partes interessadas).

🏛️ Parte 1: O Passo a Passo do Desenvolvimento
A construção do sistema seguiu uma ordem lógica de fundação, encanamento e acabamento:

A Fundação (Banco de Dados na Nuvem): Utilizamos o Oracle Cloud (Free Tier). A grande evolução aqui foi a migração para uma conexão Walletless (TLS), que elimina arquivos físicos de segurança e centraliza a autenticação em variáveis de ambiente, seguindo padrões modernos de Cloud Security.

A Modelagem (A Verdade Absoluta): Toda a estrutura física foi consolidada no artefato modelagem_fisica.sql. Desenhamos quatro estruturas blindadas com Chaves Primárias (PK):

TB_MOEDA: Cadastro das moedas (Dólar, Euro).

TB_COTACAO: Tabela fato com valor diário e volumes.

TB_TAXA_SELIC: Histórico da meta de juros (Copom).

TB_BOLETIM_FOCUS: Projeções e expectativas de mercado.

O Encanamento (Pipeline ETL): Construímos robôs em Python que consomem a API do Banco Central. A novidade é a estratégia de Higiene de Carga: o sistema realiza um TRUNCATE (limpeza) antes de cada inserção, garantindo que o banco reflita sempre a versão mais atualizada e corrigida das fontes oficiais.

O Acabamento (Frontend no Streamlit): O painel visual interativo. Ele realiza o cruzamento relacional em tempo real e foi publicado via GitHub (CI/CD), garantindo que cada melhoria no código chegue instantaneamente ao usuário final.

⚙️ Parte 2: A Engenharia de Dados (ETL)
O coração do sistema é o processo de ETL (Extract, Transform, Load):

Extração: Consulta automatizada ao "SGS" e à "PTAX" via protocolo OData.

Tratamento (Higiene de Dados): Usamos a biblioteca Pandas para desduplicação (drop_duplicates). No caso do Boletim Focus, filtramos milhares de projeções para manter apenas um registro único por data de referência, evitando conflitos na Chave Primária.

Carga (Segurança Transacional): Utilizamos a técnica executemany do driver oracledb. A carga é atômica: ou entram todos os dados limpos, ou nada entra, preservando a integridade do banco.

🧮 Parte 3: As Funcionalidades e Cálculos
O painel gera inteligência financeira baseada em dados:

Cálculo de VWAP e TWAP: Métricas institucionais que definem o "preço justo". O VWAP pondera o valor pelo volume movimentado, enquanto o TWAP dilui o preço ao longo do tempo.

Módulo de Macroeconomia: Cruza dados de Câmbio com a VALOR_TAXA (Selic) e a VALOR_EXPECTATIVA (Focus), permitindo visualizar graficamente a correlação entre juros e valorização da moeda.

Volume Sintético: Como dados de volume real da B3 são restritos, injetamos volumes calculados para homologar as funções de agregação (SUM, AVG) e os cálculos de VWAP no banco de dados.

🧠 Parte 4: Decisões Arquiteturais (O Porquê)
Por que Oracle e não NoSQL? Dados financeiros exigem ACID (Atomicidade e Consistência). As Constraints de Chave Primária no Oracle impedem que o sistema exiba dados duplicados ao investidor.

Por que Conexão Walletless (TLS)? Eliminamos a dependência de pastas de carteiras (Wallets) locais. Isso torna o sistema mais leve, seguro e fácil de hospedar em qualquer servidor de nuvem moderno.

Por que Carga Completa (Truncate)? Instituições financeiras revisam dados passados frequentemente. Ao limpar e recarregar a tabela diariamente, garantimos que nossa base de dados nunca fique com valores históricos defasados.

Segurança e .env: Aplicamos o conceito de "Zero Trust". Nenhuma senha está no código. Tudo é injetado via variáveis de ambiente, protegendo o acesso ao Oracle Cloud de ponta a ponta.

📈 Parte 5: Usabilidade e Mercado Consumidor
Público-alvo para esta arquitetura no mundo real:

Tesourarias Corporativas: Empresas que precisam de um "Benchmark" (referência) para validar se suas operações de câmbio estão próximas ao preço justo (VWAP).

Controladoria e Auditoria: O uso de um banco de dados relacional sólido como o Oracle garante que os dados usados nos relatórios sejam auditáveis e imutáveis.