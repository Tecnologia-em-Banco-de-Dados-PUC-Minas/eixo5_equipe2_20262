# ETAPA 2 — COLETA, MODELO INICIAL E GOVERNANÇA DE DADOS
1. Estratégia de Coleta de Dados

A coleta de dados deste projeto dá continuidade à infraestrutura desenvolvida no semestre anterior, reaproveitando o Data Lake e os processos de ingestão, transformação e integração já implementados.

O projeto utiliza dados públicos provenientes de três fontes principais: Operador Nacional do Sistema Elétrico (ONS), Instituto Nacional de Meteorologia (INMET) e Instituto Brasileiro de Geografia e Estatística (IBGE).

O período histórico compreende os anos de 2016 a 2024, permitindo analisar diferentes ciclos sazonais e comportamentos do sistema elétrico e fornecendo uma base histórica para o desenvolvimento dos modelos de Machine Learning.

| Fonte | Forma de acesso | Principais dados | Utilização |
|---|---|---|---|
| **ONS** | Dados públicos / Amazon S3 | Geração, carga, capacidade instalada e hidrologia | Variáveis energéticas e hidrológicas |
| **INMET** | Dados públicos / Google BigQuery | Temperatura, precipitação, vento e radiação solar | Variáveis climáticas |
| **IBGE** | Dados públicos / API | Municípios, estados e informações territoriais | Padronização e integração geográfica |

1.1. Dados do ONS

Os dados do ONS constituem a principal fonte de informações energéticas e hidrológicas do projeto. São utilizados conjuntos relacionados à geração de energia, geração por usina, capacidade instalada, carga do sistema e informações hidrológicas.

Na etapa de Machine Learning, esses dados poderão assumir dois papéis: variáveis explicativas (features), como valores históricos de carga, geração e condições hidrológicas, e variáveis-alvo (target), representando os valores que os modelos buscarão prever.

1.2. Dados do INMET

Os dados meteorológicos são provenientes das estações do INMET e incluem variáveis como temperatura, precipitação, velocidade do vento e radiação solar.

Essas informações são utilizadas para investigar a relação entre condições climáticas e o comportamento do sistema elétrico.

Os microdados possuem originalmente granularidade horária. No pipeline desenvolvido anteriormente, esses registros são tratados e agregados para granularidade diária, permitindo sua integração com as demais séries utilizadas pelo projeto.

1.3. Dados do IBGE

Os dados do IBGE são utilizados para padronização geográfica e integração entre as diferentes fontes.

A utilização de identificadores territoriais padronizados permite relacionar municípios, estados e regiões às estações meteorológicas e aos dados do sistema elétrico.

2. Processo de Ingestão e Armazenamento

O processo de ingestão utiliza a Arquitetura Medalhão (Medallion Architecture), composta pelas camadas Bronze, Silver e Gold.

```text
FONTES EXTERNAS
       │
       ├── ONS
       ├── INMET
       └── IBGE
       │
       ▼
┌─────────────────────┐
│       BRONZE        │
│     Amazon S3       │
│ Dados provenientes  │
│ das fontes          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│       SILVER        │
│ AWS Glue / PySpark  │
│ Limpeza, tipagem e  │
│ padronização        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│        GOLD         │
│   Amazon Athena     │
│ Modelo analítico    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ ANALYTICS E MACHINE │
│      LEARNING       │
│ Features e Targets  │
└─────────────────────┘
```
Na camada Bronze, os dados são preservados próximos ao formato de origem, garantindo rastreabilidade e possibilidade de reprocessamento.

Na camada Silver, são executados processos de limpeza, tipagem, tratamento de valores nulos, normalização, padronização temporal e geográfica e adequação da granularidade.

Na camada Gold, os dados são organizados em estruturas analíticas integradas, preparadas para consultas, indicadores, dashboards e construção dos datasets destinados aos modelos de Machine Learning.

Para os dados do ONS, a ingestão utiliza transferência entre buckets Amazon S3. Para os microdados do INMET, é utilizada uma estratégia Multi-Cloud, consultando os registros no Google BigQuery e transferindo os dados processados para o Amazon S3 em formato Parquet.

3. Modelo Inicial de Dados

O modelo inicial aproveita a estrutura dimensional desenvolvida no semestre anterior, organizada em dimensões e tabelas fato.

As principais dimensões são Tempo, responsável pelos atributos temporais; Localização, que organiza municípios, estados e regiões; e Usina, que contém a identificação e características das unidades geradoras.

As principais tabelas fato são Clima, Geração, Carga, Hidrologia e Eficiência Hidrelétrica.

A partir desse modelo analítico serão construídos os datasets destinados aos experimentos de Machine Learning.

```text
                    ┌───────────────┐
                    │  DIM_TEMPO    │
                    └───────┬───────┘
                            │
     ┌──────────────────────┼───────────────────────┐
     │                      │                       │
     ▼                      ▼                       ▼
┌─────────────┐      ┌─────────────┐        ┌──────────────┐
│ FATO_CLIMA  │      │ FATO_CARGA  │        │FATO_GERACAO │
└──────┬──────┘      └──────┬──────┘        └──────┬───────┘
       │                     │                      │
       └─────────────┬───────┴──────────────┬───────┘
                     │                      │
              ┌──────▼───────┐       ┌──────▼────────┐
              │DIM_LOCALIZACAO│       │  DIM_USINA    │
              └───────────────┘       └───────┬───────┘
                                             │
                                      ┌──────▼──────────┐
                                      │ FATO_HIDROLOGIA │
                                      └─────────────────┘
```

Para Machine Learning, os dados provenientes dessas estruturas serão reorganizados de acordo com o problema preditivo.

As features poderão incluir variáveis climáticas, hidrológicas e temporais, além de valores históricos de carga e geração. As variáveis-alvo (targets) poderão representar, por exemplo, a carga futura do sistema ou a geração futura de energia.

Também poderão ser construídas variáveis derivadas, como valores defasados (lags), médias móveis e atributos de calendário.

4. Estratégia de Governança de Dados

A governança de dados do projeto tem como objetivo assegurar que os dados utilizados durante todo o ciclo de vida sejam confiáveis, rastreáveis, consistentes, documentados e adequados para análise e Machine Learning.

A estratégia será orientada pelos princípios de qualidade, garantindo consistência, completude e validade; rastreabilidade, permitindo identificar a origem e as transformações dos dados; padronização, estabelecendo padrões de nomenclatura, formatos e tipos; e documentação, registrando fontes, schemas e regras de transformação.

Também serão considerados os princípios de segurança, por meio do controle de acesso aos recursos; disponibilidade, garantindo acesso aos dados necessários; reprodutibilidade, possibilitando a reexecução dos processos; e confiabilidade analítica, assegurando que os dados utilizados pelos modelos representem adequadamente o fenômeno e o período analisados.

5. Governança no Ciclo de Vida dos Dados

A governança será aplicada durante todo o ciclo de vida dos dados, desde sua obtenção até a utilização nos modelos de Machine Learning e produtos analíticos.

```text

COLETA
   ↓
INGESTÃO
   ↓
ARMAZENAMENTO
   ↓
TRATAMENTO
   ↓
INTEGRAÇÃO
   ↓
EXPLORAÇÃO E PREPARAÇÃO
   ↓
MACHINE LEARNING
   ↓
CONSUMO DOS RESULTADOS
   ↓
MONITORAMENTO E ATUALIZAÇÃO

```

Na coleta, as fontes serão identificadas e documentadas, registrando instituição responsável, conjunto de dados, período disponível, forma de acesso e principais variáveis.

Na ingestão e armazenamento, os dados provenientes das fontes serão inicialmente armazenados na camada Bronze. A preservação desses registros permite manter uma referência dos dados obtidos e realizar novos processamentos quando necessário.

No tratamento, realizado na camada Silver, serão aplicadas regras de qualidade, incluindo tratamento de valores nulos, conversão de tipos, padronização de datas, normalização de valores e compatibilização das granularidades.

Na integração, os conjuntos serão relacionados por dimensões comuns, especialmente tempo e localização, permitindo integrar informações climáticas, energéticas e hidrológicas.

Na exploração e preparação para Machine Learning, os dados serão analisados quanto à distribuição, completude, presença de anomalias e consistência temporal. Nessa fase também serão construídas as features necessárias para os experimentos.

Na etapa de Machine Learning, os datasets utilizados deverão possuir identificação das variáveis e períodos considerados. A divisão entre treinamento, validação e teste respeitará a ordem temporal das observações, evitando a utilização indevida de informações futuras.

No consumo, os resultados poderão ser disponibilizados por meio de tabelas analíticas, métricas de desempenho, previsões e dashboards.

Por fim, o monitoramento e atualização deverá permitir a inclusão de novos períodos de dados e a reexecução das etapas de processamento sem geração de registros duplicados.

6. Requisitos e Procedimentos de Governança

Para garantir a qualidade e a confiabilidade dos dados, serão definidos requisitos e procedimentos aplicáveis às diferentes etapas do projeto.

| Requisito | Procedimento |
|---|---|
| **Origem confiável** | Utilizar fontes públicas oficiais e documentar a procedência dos dados |
| **Integridade** | Verificar arquivos incompletos, registros inválidos e falhas de ingestão |
| **Completude** | Identificar valores nulos e lacunas nas séries temporais |
| **Unicidade** | Identificar e tratar registros duplicados |
| **Consistência** | Padronizar tipos, unidades, datas e identificadores |
| **Rastreabilidade** | Manter separação entre Bronze, Silver e Gold e documentar transformações |
| **Padronização** | Adotar padrões de nomenclatura para tabelas, campos, arquivos e partições |
| **Documentação** | Manter dicionários de dados e schemas das principais estruturas |
| **Reprodutibilidade** | Versionar scripts e permitir reexecução dos pipelines |
| **Segurança** | Restringir permissões de acordo com a necessidade de acesso |
| **Qualidade para ML** | Validar features, targets e períodos utilizados nos modelos |
| **Prevenção de vazamento temporal** | Garantir que dados futuros não sejam utilizados para prever períodos anteriores |
| **Monitoramento** | Registrar execuções, erros e resultados dos processos |

7. Papéis e Responsabilidades

Mesmo tratando-se de um projeto acadêmico, são definidos papéis de governança para estabelecer responsabilidades ao longo do ciclo de vida dos dados.

O Data Owner é responsável por definir as necessidades do projeto, os objetivos de utilização dos dados e os critérios gerais de acesso e uso.

O Data Engineer é responsável pelos processos de coleta, ingestão, armazenamento, transformação e integração dos dados, além da manutenção dos pipelines.

O Data Steward acompanha a qualidade, padronização, documentação, significado e consistência dos dados.

O Data Scientist é responsável pela análise exploratória, preparação das features, construção dos datasets, treinamento, validação e avaliação dos modelos de Machine Learning.

O Data Consumer representa os usuários das informações produzidas pelo projeto, incluindo aqueles que utilizarão dashboards, indicadores, análises e previsões para apoiar a tomada de decisão.

8. Matriz de Governança

A matriz de governança relaciona as principais etapas do ciclo de vida dos dados aos requisitos, procedimentos e responsabilidades definidos para o projeto.

| Etapa | Requisito | Procedimento | Responsável |
|---|---|---|---|
| **Coleta** | Confiabilidade | Validar e documentar as fontes | Data Engineer / Data Steward |
| **Bronze** | Rastreabilidade | Preservar os dados provenientes das fontes | Data Engineer |
| **Silver** | Qualidade | Limpar, tipar, padronizar e validar os registros | Data Engineer / Data Steward |
| **Gold** | Consistência | Validar integrações, dimensões, fatos e indicadores | Data Engineer / Data Steward |
| **Preparação para ML** | Qualidade analítica | Criar e validar features e targets | Data Scientist |
| **Treinamento** | Reprodutibilidade | Registrar dados, variáveis e configurações dos experimentos | Data Scientist |
| **Validação e teste** | Confiabilidade | Avaliar modelos em períodos não utilizados no treinamento | Data Scientist |
| **Consumo** | Acessibilidade | Disponibilizar indicadores, previsões e resultados autorizados | Data Owner / Data Consumer |
| **Monitoramento** | Continuidade | Acompanhar execuções, falhas, qualidade e atualizações | Data Engineer |

9. Qualidade dos Dados

Antes de serem utilizados nas análises e nos modelos de Machine Learning, os dados serão avaliados quanto à qualidade.

Serão verificados valores nulos, registros duplicados, inconsistências de tipos, lacunas temporais, valores fora das faixas esperadas, divergências de granularidade e incompatibilidades entre identificadores geográficos.

Também será avaliada a cobertura histórica das diferentes variáveis, considerando que nem todas as fontes necessariamente apresentam a mesma disponibilidade para todo o período de 2016 a 2024.

Os problemas identificados deverão ser registrados e tratados de maneira reproduzível durante a transformação dos dados.

10. Documentação, Versionamento e Rastreabilidade

A documentação faz parte da estratégia de governança do projeto. Os schemas e dicionários de dados deverão registrar, sempre que aplicável, o nome e a descrição do campo, tipo de dado, fonte, unidade de medida, granularidade, regra de transformação e utilização analítica.

Os códigos responsáveis pela ingestão, transformação, criação das tabelas e experimentos de Machine Learning serão versionados no GitHub, permitindo acompanhar as alterações realizadas durante o desenvolvimento.

A organização em camadas Bronze, Silver e Gold também contribuirá para a rastreabilidade, permitindo identificar o caminho percorrido pelo dado desde sua origem até sua utilização analítica.

Nos experimentos de Machine Learning, deverão ser registrados o conjunto de dados utilizado, as features, a variável-alvo, os períodos de treinamento, validação e teste, o algoritmo empregado, seus principais parâmetros e as métricas obtidas.

11. Resultado Esperado da Etapa

Ao final desta etapa, espera-se estabelecer uma estrutura de coleta e governança capaz de acompanhar todo o ciclo de vida dos dados utilizados no projeto.

A continuidade da arquitetura desenvolvida anteriormente permitirá reaproveitar os dados históricos e os processos já implementados, enquanto a formalização das regras de governança deverá aumentar a rastreabilidade, a qualidade e a confiabilidade das informações.

A estrutura resultante deverá fornecer uma base adequada para a próxima fase do projeto, permitindo que os dados armazenados e tratados sejam utilizados de maneira controlada e reproduzível na análise exploratória e no desenvolvimento dos modelos de Machine Learning.

O fluxo final pode ser sintetizado da seguinte maneira:

```text

FONTES
   ↓
COLETA
   ↓
BRONZE
   ↓
SILVER
   ↓
GOLD
   ↓
DATASET DE MACHINE LEARNING
   ↓
MODELO
   ↓
PREVISÕES E ANÁLISES
```

