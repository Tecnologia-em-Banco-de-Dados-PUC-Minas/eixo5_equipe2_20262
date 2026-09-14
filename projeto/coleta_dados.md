ETAPA 2 — COLETA DE DADOS
1. Estratégia de Coleta de Dados

A etapa de coleta de dados dará continuidade à infraestrutura desenvolvida no semestre anterior, aproveitando o Data Lake já estruturado na Amazon Web Services (AWS) e as rotinas de ingestão criadas para integração das diferentes fontes de dados.

A nova fase do projeto terá como foco não apenas disponibilizar os dados para análises descritivas, mas também garantir que as informações coletadas possuam qualidade, granularidade e histórico suficientes para utilização em modelos de Machine Learning.

Serão utilizados dados públicos provenientes do Operador Nacional do Sistema Elétrico (ONS), do Instituto Nacional de Meteorologia (INMET) e do Instituto Brasileiro de Geografia e Estatística (IBGE). Essas fontes permitem combinar informações energéticas, climáticas, hidrológicas e geográficas em uma base integrada.

O período histórico principal compreende os anos de 2016 a 2024, totalizando nove anos de informações. A utilização desse intervalo permite trabalhar com diferentes ciclos sazonais, condições climáticas e comportamentos do sistema elétrico, criando uma base adequada para análise exploratória e desenvolvimento dos modelos preditivos.

2. Fontes de Dados

As fontes utilizadas no projeto são apresentadas a seguir:

| Fonte | Tipo de acesso | Principais dados | Utilização no projeto |
|---|---|---|---|
| **ONS — Operador Nacional do Sistema Elétrico** | Dados públicos / Amazon S3 | Geração de energia, geração por usina, capacidade instalada, carga do sistema e dados hidrológicos | Variáveis energéticas e hidrológicas, incluindo possíveis variáveis-alvo dos modelos |
| **INMET — Instituto Nacional de Meteorologia** | Dados públicos / Google BigQuery | Temperatura, precipitação, velocidade do vento, radiação solar e informações das estações meteorológicas | Variáveis climáticas utilizadas como atributos explicativos |
| **IBGE — Instituto Brasileiro de Geografia e Estatística** | Dados públicos / API e diretórios geográficos | Municípios, estados e informações territoriais | Padronização e integração geográfica entre estações meteorológicas, regiões e dados energéticos |

2.1. Dados do ONS

Os dados do Operador Nacional do Sistema Elétrico constituem a principal fonte de informações energéticas e hidrológicas do projeto.

Serão utilizados conjuntos relacionados a:

geração de energia por usina;
capacidade instalada de geração;
modalidade e tipo de geração;
carga de energia do sistema;
dados hidrológicos dos reservatórios e usinas.

Essas informações permitem analisar o comportamento histórico do Sistema Interligado Nacional e construir variáveis relacionadas à produção e ao consumo de energia.

Para a etapa de Machine Learning, os dados do ONS poderão assumir dois papéis distintos. Parte das informações será utilizada como variável-alvo, representando o comportamento que se deseja prever, enquanto outras poderão ser utilizadas como variáveis explicativas, especialmente valores históricos de carga, geração e condições hidrológicas.

Um exemplo é a utilização da carga histórica do sistema para previsão da carga futura. Da mesma forma, dados de vazão, armazenamento e geração histórica poderão ser utilizados em análises relacionadas à previsão da geração hidrelétrica.

2.2. Dados do INMET

Os dados meteorológicos utilizados são provenientes das estações do Instituto Nacional de Meteorologia.

Entre as principais variáveis disponíveis para utilização no projeto estão:

temperatura;
precipitação;
velocidade do vento;
radiação solar;
localização das estações;
data e horário das medições.

Essas informações possuem importância direta para o problema proposto, uma vez que diferentes fontes de geração de energia apresentam dependência das condições climáticas.

A velocidade do vento possui relação com o potencial de geração eólica, enquanto a radiação solar está associada à geração fotovoltaica. A precipitação pode contribuir para a análise da disponibilidade hídrica e a temperatura pode apresentar relação tanto com as condições ambientais quanto com o comportamento da demanda de energia.

Os dados originalmente possuem granularidade horária. Na infraestrutura desenvolvida anteriormente, essas informações foram agregadas para granularidade diária, utilizando soma para precipitação e médias para variáveis como temperatura, vento e radiação.

Essa granularidade será inicialmente mantida para os experimentos de Machine Learning, permitindo compatibilizar os registros climáticos com as demais séries temporais utilizadas no projeto.

2.3. Dados do IBGE

Os dados do IBGE serão utilizados como suporte para integração geográfica.

A associação entre informações climáticas e energéticas exige que diferentes identificadores territoriais sejam padronizados. As estações meteorológicas possuem localização própria, enquanto informações do sistema elétrico podem estar relacionadas a municípios, estados, regiões, subsistemas ou usinas.

O diretório de municípios permite criar uma dimensão geográfica comum, facilitando o relacionamento entre as diferentes fontes.

Esses dados também poderão ser utilizados posteriormente para criação de atributos geográficos e para segmentação das análises e previsões por unidade federativa ou região.
