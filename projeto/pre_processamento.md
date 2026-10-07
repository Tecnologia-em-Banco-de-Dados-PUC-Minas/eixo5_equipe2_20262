# 3. PRÉ-PROCESSAMENTO DE DADOS

O pré-processamento dos dados teve como objetivo preparar as informações provenientes das fontes climáticas e elétricas para utilização na camada analítica do projeto Energia & Clima. Essa etapa envolveu a organização, padronização, integração e validação dos dados, buscando garantir maior consistência, rastreabilidade e qualidade das informações utilizadas nas análises posteriores.

O processamento foi estruturado segundo uma arquitetura em camadas, na qual os dados brutos foram inicialmente armazenados na camada Bronze, posteriormente tratados e organizados na camada Silver e, por fim, integrados em estruturas analíticas na camada Gold. O armazenamento foi realizado no Amazon S3, enquanto o processamento e a catalogação dos dados utilizaram recursos da AWS, principalmente AWS Glue, Glue Data Catalog e Amazon Athena.

## 3.1 Padronização estrutural

A primeira etapa do pré-processamento consistiu na padronização estrutural dos dados provenientes das diferentes fontes utilizadas no projeto. Foram consideradas informações provenientes do Operador Nacional do Sistema Elétrico (ONS), do Instituto Nacional de Meteorologia (INMET) e de diretórios auxiliares utilizados para complementar informações geográficas.

Os dados foram armazenados inicialmente em seu formato bruto na camada Bronze. Na camada Silver, foram realizadas transformações para padronização dos nomes das colunas, tipos de dados e representação das datas, além da organização dos arquivos em formato Parquet e da utilização de particionamento por ano e mês nas tabelas que possuem séries temporais.

As datas foram padronizadas no campo event_date, permitindo a integração temporal entre diferentes conjuntos de dados. Os dados de carga, geração e hidrologia apresentam cobertura diária contínua entre 2016 e 2024, enquanto os dados meteorológicos possuem período de cobertura entre dezembro de 2015 e novembro de 2024.

Após o tratamento, os dados foram catalogados no AWS Glue Data Catalog, possibilitando sua consulta por meio do Amazon Athena.

## 3.2 Tratamento de duplicidades

O tratamento de duplicidades foi realizado por meio da análise da quantidade de registros e das chaves utilizadas para representar a granularidade de cada conjunto de dados.

As tabelas de carga e clima apresentaram correspondência entre os registros das camadas Silver e Gold, sem diferenças nas validações realizadas. A mesma correspondência foi observada para geração e hidrologia.

É importante destacar que geração e hidrologia possuem granularidade mais detalhada, portanto, a existência de mais de um registro para uma combinação simplificada de campos não caracteriza necessariamente uma duplicidade. Dessa forma, a validação considerou a granularidade original dos dados, evitando a remoção indevida de registros legítimos.

Como resultado, não foram identificadas diferenças entre os registros das camadas Silver e Gold nas validações realizadas.

## 3.3 Tratamento de valores ausentes

A análise de valores ausentes foi realizada principalmente sobre as variáveis meteorológicas. Foram identificados valores nulos nas informações provenientes do INMET, situação esperada devido às diferenças de disponibilidade e continuidade das medições entre as estações meteorológicas.

Na tabela de fatos climáticos, foram identificados:

* 364.704 valores nulos de precipitação, correspondendo a aproximadamente 21,41% dos registros;
* 279.592 valores nulos de radiação global, correspondendo a aproximadamente 16,41%;
* 255.041 valores nulos nas variáveis de temperatura, correspondendo a aproximadamente 14,97%;
* 311.196 valores nulos de velocidade média do vento, correspondendo a aproximadamente 18,27%.

* Os valores ausentes foram mantidos na camada analítica, preservando a informação original e evitando a introdução de valores artificiais por meio de imputações não fundamentadas.

Por outro lado, as tabelas de carga e geração não apresentaram valores nulos nas principais chaves e campos de data analisados.

## 3.4 Tratamento de valores fora da faixa esperada

Foram realizadas verificações de consistência sobre variáveis numéricas, utilizando faixas consideradas plausíveis para cada tipo de informação.

Nas variáveis meteorológicas foram identificados 333 registros de temperatura máxima, 336 registros de temperatura média e 336 registros de temperatura mínima fora da faixa de referência utilizada na validação. Dessa forma, foram identificados 1.005 ocorrências relacionadas às variáveis de temperatura.

Para precipitação, velocidade do vento e radiação global não foram identificados valores negativos. Também não foram identificados valores negativos de geração ou valores inválidos de carga nas verificações realizadas.

Os valores fora da faixa foram identificados e registrados durante a etapa de validação da qualidade dos dados. Eles não foram automaticamente convertidos para nulo, uma vez que a substituição desses valores exigiria uma regra de tratamento específica e validada para a fonte meteorológica.

## 3.5 Granularidade dos dados

A definição da granularidade foi considerada fundamental para evitar agregações ou eliminações indevidas durante a integração dos dados.

A tabela gold_fato_carga apresenta informações em granularidade diária por subsistema. A tabela gold_fato_geracao apresenta dados diários relacionados ao subsistema, estado e tipo de usina. A tabela gold_fato_hidrologia apresenta informações diárias por reservatório, contemplando variáveis relacionadas ao nível, volume e vazões.

Já a tabela gold_fato_clima mantém a granularidade diária por estação meteorológica, permitindo relacionar as condições climáticas observadas com informações temporais e geográficas.

A manutenção dessas granularidades permite que análises posteriores sejam realizadas sem perda da informação original e possibilita diferentes níveis de agregação conforme a necessidade analítica.

## 3.6 Padronização geográfica

Para possibilitar a integração das informações meteorológicas com dados geográficos, foram utilizadas as tabelas de estações meteorológicas e diretórios de municípios brasileiros.

A dimensão gold_dim_localizacao foi construída integrando informações como identificador da estação, município, unidade federativa, região, altitude e data de fundação da estação.

A dimensão resultante contém 633 registros e apresentou ausência de valores nulos nas principais chaves analisadas, incluindo identificador da estação e município.

Essa padronização permite associar os dados meteorológicos às respectivas localidades e possibilita análises futuras por município, estado e região.

## 3.7 Tratamento de variáveis categóricas e escala

As variáveis categóricas utilizadas nas análises, como tipo de usina, subsistema, estado e região, foram mantidas em formato textual padronizado nas tabelas analíticas.

Nesta etapa do projeto não foi realizada aplicação de técnicas de normalização ou padronização estatística das variáveis numéricas, nem transformação das categorias por one-hot encoding. Essas técnicas são mais adequadas a etapas posteriores de modelagem estatística ou aprendizado de máquina, caso sejam necessárias.

Dessa forma, a camada Gold mantém os valores numéricos em sua representação original, permitindo sua utilização tanto em análises descritivas quanto em futuras etapas de modelagem.

# 4. INTEGRAÇÃO E RELACIONAMENTOS

## 4.1 Chaves e cardinalidade

A integração dos dados foi estruturada a partir de dimensões e tabelas fato, seguindo uma organização dimensional.

Entre as principais estruturas estão a dimensão de tempo (gold_dim_tempo), a dimensão de localização (gold_dim_localizacao) e a dimensão de usinas (gold_dim_usina). As tabelas fato armazenam as informações relacionadas a carga, clima, geração e hidrologia.

Foram realizadas validações para verificar a existência de valores nulos nas principais chaves. Não foram identificadas chaves nulas nas dimensões e fatos analisados.

A dimensão de tempo possui 3.289 datas distintas, abrangendo o período de 31/12/2015 a 31/12/2024, enquanto as principais séries elétricas possuem cobertura diária completa de 2016 a 2024.

## 4.2 Relacionamento e integração das fontes

A integração foi realizada utilizando atributos temporais, geográficos e identificadores específicos de cada domínio.

Os dados climáticos foram relacionados às informações das estações meteorológicas e dos municípios por meio dos identificadores das estações e municípios. Os dados elétricos foram organizados a partir de identificadores de subsistema, estado, usina e reservatório, conforme a granularidade de cada fonte.

O campo event_date foi utilizado como referência temporal comum entre as diferentes fontes, possibilitando posteriormente a realização de análises integradas entre condições climáticas, carga elétrica, geração e informações hidrológicas.

## 4.3 Datasets analíticos resultantes

Ao final do processamento foi construída a camada Gold, composta por sete estruturas analíticas:

| Tabela                 |     Registros |
| ---------------------- | ------------: |
| gold_dim_localizacao |           633 |
| gold_dim_tempo       |         3.289 |
| gold_dim_usina       |         4.026 |
| gold_fato_carga      |        13.152 |
| gold_fato_clima      |     1.703.674 |
| gold_fato_geracao    |       231.126 |
| gold_fato_hidrologia |       605.802 |
| *Total*              | *2.561.702* |

As estruturas resultantes permitem a realização de análises integradas entre informações meteorológicas, geração de energia, carga do sistema e condições hidrológicas.

As validações realizadas entre as camadas Silver e Gold não identificaram diferenças nos conjuntos de dados de carga, geração, hidrologia e clima.

## 4.4 Organização temporal dos dados

Os dados elétricos de carga, geração e hidrologia apresentam cobertura diária contínua entre 01/01/2016 e 31/12/2024, totalizando 3.288 dias.

s tabelas de carga, geração e hidrologia apresentaram cobertura completa para esse período, não sendo identificados dias sem registros nas verificações realizadas.

A dimensão de tempo foi estruturada para permitir análises por ano, trimestre, mês, dia da semana e identificação de finais de semana.

A divisão temporal entre períodos de treinamento, validação e teste poderá ser utilizada posteriormente em aplicações de modelagem preditiva. Como o objetivo desta etapa foi o processamento e a validação dos dados, essa divisão não representa a execução de modelos de aprendizado de máquina neste momento.

# 5. VALIDAÇÃO DA QUALIDADE PÓS-TRATAMENTO

Após a construção da camada Gold, foram realizadas validações para verificar a consistência estrutural, temporal e referencial dos dados.

A camada Gold contém 2.561.702 registros distribuídos em sete tabelas. As principais dimensões e tabelas fato não apresentaram valores nulos em suas chaves analisadas.

As tabelas de carga, geração e hidrologia apresentaram cobertura diária completa entre 2016 e 2024. Além disso, foram realizadas comparações entre Silver e Gold, não sendo identificadas diferenças nos registros das quatro principais tabelas fato analisadas.

A tabela abaixo resume os principais resultados da validação:

| Indicador de qualidade                                           | Resultado |
| ---------------------------------------------------------------- | --------: |
| Tabelas na camada Gold                                           |         7 |
| Registros na camada Gold                                         | 2.561.702 |
| Diferenças entre Silver e Gold                                   |         0 |
| Chaves nulas nas estruturas principais                           |         0 |
| Dias sem registro de carga (2016–2024)                           |         0 |
| Dias sem registro de geração (2016–2024)                         |         0 |
| Dias sem registro de hidrologia (2016–2024)                      |         0 |
| Nulos de precipitação                                            |    21,41% |
| Nulos de radiação global                                         |    16,41% |
| Nulos de temperatura                                             |    14,97% |
| Nulos de velocidade do vento                                     |    18,27% |
| Valores de temperatura fora da faixa de referência identificados |     1.005 |
| Estações meteorológicas na camada Gold                           |       633 |
| Estações com alta cobertura temporal                             |       472 |

No caso das estações meteorológicas, 472 apresentaram alta cobertura segundo o critério utilizado na análise, enquanto as demais foram mantidas na camada Gold para preservar a rastreabilidade e a informação original. Portanto, não foram consideradas estações descartadas durante o processamento.

Os valores ausentes e os valores fora das faixas de referência foram mantidos identificados para possibilitar tratamentos específicos em análises posteriores, evitando alterações automáticas sem justificativa metodológica.


# 6. FERRAMENTAS UTILIZADAS

O processamento foi realizado utilizando serviços da Amazon Web Services (AWS).

O Amazon S3 foi utilizado como camada de armazenamento dos dados, organizando os arquivos segundo as camadas Bronze e Silver e posteriormente disponibilizando os dados tratados para a camada Gold.

O AWS Glue foi utilizado para processamento e transformação dos dados, além da criação e execução dos processos responsáveis pela preparação da camada Silver.

O AWS Glue Data Catalog foi utilizado para catalogação das tabelas e organização dos metadados. Para facilitar a descoberta das estruturas armazenadas na camada Silver, foi utilizado um crawler responsável pela identificação dos arquivos e criação das tabelas no catálogo.

O Amazon Athena foi utilizado para consultas SQL, validações, análises exploratórias e conferência da consistência entre as camadas Silver e Gold.

# 7. FLUXO DO PRÉ-PROCESSAMENTO

O fluxo de processamento desenvolvido pode ser representado da seguinte forma:

*Fontes de dados → Camada Bronze → Amazon S3 → AWS Glue → Camada Silver → Glue Data Catalog → Camada Gold → Amazon Athena → Análise*

Inicialmente, os dados provenientes das fontes ONS e INMET são armazenados na camada Bronze em seu formato original. Em seguida, os dados são processados pelo AWS Glue, passando por padronização estrutural, organização dos tipos de dados, tratamento das datas e estruturação em formato adequado para consulta.

Os dados processados são disponibilizados na camada Silver, armazenada no Amazon S3 em formato Parquet e organizada por partições temporais quando aplicável.

Posteriormente, os dados são integrados e organizados na camada Gold, composta por dimensões e tabelas fato. O Glue Data Catalog disponibiliza os metadados dessas estruturas e o Amazon Athena permite a realização das consultas e validações.

Esse fluxo proporciona separação entre dados brutos, dados tratados e dados analíticos, facilitando a rastreabilidade e a manutenção da arquitetura.

# 8. RESULTADOS DO PRÉ-PROCESSAMENTO

Ao final do pré-processamento, os dados provenientes das diferentes fontes foram organizados em uma arquitetura de dados composta pelas camadas Bronze, Silver e Gold.

A camada Gold resultou em sete estruturas analíticas, totalizando 2.561.702 registros. As tabelas apresentam informações de localização, tempo, usinas, carga elétrica, clima, geração de energia e hidrologia.

As validações realizadas demonstraram consistência entre os dados das camadas Silver e Gold, sem diferenças nos conjuntos de dados comparados. Também não foram identificadas chaves nulas nas principais estruturas analisadas e as séries de carga, geração e hidrologia apresentaram cobertura diária completa entre 2016 e 2024.

Foram identificadas limitações principalmente relacionadas à disponibilidade dos dados meteorológicos, que apresentam valores ausentes e diferentes níveis de cobertura entre as estações. Essas características foram preservadas na camada analítica para evitar a introdução de valores artificiais sem uma metodologia de imputação definida.

Dessa forma, o pré-processamento produziu uma base estruturada e validada para as etapas posteriores do projeto, permitindo a realização de análises integradas entre variáveis climáticas, geração de energia, carga elétrica e condições hidrológicas.
=======
Etapa 3
