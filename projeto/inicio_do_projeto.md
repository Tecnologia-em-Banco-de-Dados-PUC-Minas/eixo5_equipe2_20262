**ETAPA 1**  

### TÍTULO DO PROJETO:  

Análise Integrada de Dados Climáticos e Elétricos Utilizando Big Data Analytics   
 

**1\. Motivação da Escolha do Tema**

Como grupo, decidimos dar continuidade ao tema Energia & Clima por entendermos que ele representa um cenário relevante e desafiador para a aplicação integrada de conceitos de Big Data Analytics e Machine Learning. A etapa anterior permitiu estruturar uma arquitetura de dados capaz de integrar informações climáticas, hidrológicas e elétricas, criando uma base consistente para a evolução do projeto em direção a análises preditivas.

A continuidade proposta busca ampliar a capacidade analítica da solução, avançando da identificação de padrões históricos e relações entre variáveis para a construção de modelos capazes de estimar comportamentos futuros da geração e da demanda de energia elétrica.

**1.1 Aderência aos “Vs” do Big Data (Volume, Velocidade e Variedade)**

O setor elétrico brasileiro e o monitoramento climático geram continuamente grandes volumes de dados, provenientes de diferentes fontes e apresentados em distintas granularidades temporais e formatos. O projeto utiliza bases públicas de instituições como o Operador Nacional do Sistema Elétrico (ONS) e o Instituto Nacional de Meteorologia (INMET), contendo séries temporais relacionadas à geração, carga, hidrologia e condições meteorológicas.

A diversidade, o volume e a frequência dessas informações tornam o cenário adequado para aplicação de técnicas de Big Data, exigindo processos de ingestão, armazenamento, tratamento, integração e processamento capazes de garantir qualidade e consistência para análises avançadas.

**1.2. Relevância Socioeconômica e Prática**

A matriz elétrica brasileira possui participação significativa de fontes renováveis, como hidrelétrica, eólica e solar, fazendo com que a disponibilidade e o desempenho dessas fontes sejam diretamente influenciados por condições ambientais e climáticas.

Variáveis como precipitação, temperatura, velocidade do vento e radiação solar apresentam relação com a geração de energia, enquanto fatores climáticos também podem influenciar o comportamento da demanda elétrica. A compreensão dessas relações é relevante para o planejamento e para a segurança energética, especialmente diante do crescimento da participação das fontes renováveis no sistema elétrico brasileiro.

Nesse contexto, a utilização de Machine Learning amplia o potencial do projeto ao permitir que padrões identificados nos dados históricos sejam utilizados para estimar comportamentos futuros, oferecendo uma camada adicional de apoio à tomada de decisão.

**1.3. Desafio Técnico de Integração de Dados**

O cruzamento de dados climáticos, hidrológicos e elétricos apresenta desafios relacionados principalmente às diferenças de granularidade temporal, localização geográfica, qualidade dos registros e padronização das diferentes fontes.

Dados meteorológicos provenientes de estações precisam ser associados às regiões, usinas e demais estruturas do sistema elétrico, exigindo processos de tratamento, modelagem e integração.

A continuidade do projeto acrescenta um novo desafio técnico: preparar essas informações para utilização em modelos de Machine Learning. Isso envolve análise exploratória, tratamento de valores ausentes e anômalos, seleção de variáveis, criação de atributos derivados de séries temporais e definição adequada das variáveis que serão previstas pelos modelos.

**1.4. Potencial Preditivo dos Dados**

A existência de séries históricas integradas de clima, geração, carga e hidrologia cria condições para avançar de uma abordagem predominantemente descritiva e diagnóstica para uma abordagem preditiva.

A análise histórica permite identificar sazonalidades, tendências, correlações e comportamentos recorrentes. A partir desses padrões, técnicas de Machine Learning podem ser utilizadas para estimar variáveis futuras do sistema elétrico e avaliar quais fatores apresentam maior influência sobre essas previsões.

Essa evolução permite transformar a infraestrutura de dados já desenvolvida em uma solução capaz não apenas de explicar o comportamento histórico do sistema, mas também de gerar informações úteis para antecipação de cenários

**2\. Contexto do Problema e Cliente**

O projeto considera como cliente fictício o Operador Nacional do Sistema Elétrico (ONS), entidade responsável pela coordenação e controle da operação das instalações de geração e transmissão de energia elétrica no Sistema Interligado Nacional.

Sua atuação exige a manutenção contínua do equilíbrio entre oferta e demanda de energia, assegurando estabilidade, confiabilidade e segurança operacional.

Na etapa anterior do projeto, foram integradas informações relacionadas à geração de energia, carga do sistema, condições climáticas e variáveis hidrológicas, permitindo analisar relações entre clima e desempenho energético.

Entre os aspectos considerados estão o comportamento dos reservatórios, vazões de entrada e saída, geração das usinas, disponibilidade de recursos hídricos e influência de variáveis climáticas sobre diferentes fontes de geração.

A continuidade do projeto busca ampliar essa capacidade analítica por meio da utilização de Machine Learning. A proposta consiste em utilizar o histórico disponível para identificar padrões e desenvolver modelos capazes de estimar o comportamento futuro de variáveis relevantes do sistema elétrico.

Dessa forma, a questão central de análise passa a ser:

Como dados históricos climáticos, hidrológicos e elétricos podem ser utilizados para identificar padrões e construir modelos de Machine Learning capazes de prever o comportamento da geração e da demanda de energia elétrica, apoiando decisões operacionais no Sistema Interligado Nacional?

A partir dessa questão, o projeto pretende explorar a capacidade preditiva das informações já integradas, estabelecendo relações entre variáveis ambientais, hidrológicas, temporais e energéticas.

Além da análise histórica já desenvolvida, a solução deverá permitir comparar valores observados e previstos, avaliar o desempenho dos modelos construídos e identificar os fatores que mais contribuem para as previsões realizadas.

3. Objetivo Geral
   
**3\. Objetivo Geral**

Desenvolver uma solução analítica e preditiva baseada em Big Data Analytics e Machine Learning capaz de integrar e explorar dados climáticos, hidrológicos e energéticos, identificar padrões históricos e construir modelos de previsão do comportamento da geração e da demanda elétrica, contribuindo para a tomada de decisão operacional no contexto do Operador Nacional do Sistema Elétrico.

**3.1. Objetivos Específicos**

* Realizar a integração e consolidação dos dados provenientes de fontes públicas relacionadas à geração, carga do sistema, hidrologia e condições climáticas.
* Avaliar a qualidade, completude e consistência temporal das informações utilizadas na construção dos modelos.
* Realizar análise exploratória dos dados para identificar tendências, sazonalidades, correlações, anomalias e padrões relevantes.
* Desenvolver atributos derivados das séries temporais, incluindo informações de calendário, defasagens temporais e médias móveis, quando aplicáveis.
* Identificar as variáveis climáticas, hidrológicas e energéticas com maior potencial explicativo e preditivo.
* Desenvolver modelos de Machine Learning voltados à previsão de variáveis relacionadas ao sistema elétrico.
* Comparar diferentes algoritmos e abordagens de previsão, avaliando sua capacidade de generalização.
* Avaliar os modelos por meio de métricas quantitativas adequadas ao problema, como MAE, RMSE, MAPE e coeficiente de determinação R².
* Analisar a importância e a contribuição das diferentes variáveis utilizadas pelos modelos para a obtenção das previsões.
* Disponibilizar os resultados preditivos em ambiente analítico, permitindo a comparação entre valores reais e previstos.
* Utilizar as informações geradas pelos modelos para apoiar a compreensão do comportamento futuro do sistema e subsidiar processos de tomada de decisão baseada em dados.

**4\. Definição das Métricas e Indicadores de Análise**

Para viabilizar a análise proposta, foram definidas métricas provenientes de duas categorias principais: dados elétricos e dados climáticos. As métricas elétricas incluem a geração total de energia (MW), a geração por fonte — especialmente hidrelétrica, eólica e solar — e a carga do sistema elétrico, que representa a demanda total de energia em determinado período.

No campo climático, serão utilizadas métricas como temperatura média, velocidade do vento, radiação solar e precipitação (chuva), por serem variáveis diretamente relacionadas ao comportamento das principais fontes renováveis da matriz energética brasileira.

A partir dessas métricas, serão construídos indicadores analíticos que permitam compreender a relação entre condições climáticas e geração ou demanda de energia. Entre os principais indicadores previstos estão: a correlação entre velocidade do vento e geração eólica, o impacto da radiação solar na geração fotovoltaica, a relação entre precipitação e geração hidrelétrica e a influência da temperatura na demanda elétrica. Esses indicadores permitirão identificar padrões, dependências e possíveis tendências entre variáveis ambientais e energéticas. 

**4.1. Hipóteses de Análise

A continuidade do projeto será orientada pelas seguintes hipóteses:

H1: A incorporação de variáveis climáticas aos dados históricos de carga contribui para melhorar a capacidade de previsão da demanda de energia elétrica.

H2: Variáveis relacionadas à precipitação, vazão e armazenamento apresentam capacidade explicativa e preditiva sobre o comportamento da geração hidrelétrica.

H3: A utilização de atributos temporais, como mês, dia da semana, sazonalidade e valores históricos defasados, aumenta a capacidade preditiva dos modelos.

H4: Modelos capazes de representar relações não lineares entre as variáveis podem apresentar desempenho superior a modelos lineares simples.

H5: A análise da importância das variáveis utilizadas pelos modelos permitirá identificar quais fatores climáticos, hidrológicos e temporais apresentam maior contribuição para as previsões energéticas.

**5\. Recorte Temporal da Análise**

Na etapa anterior do projeto foi inicialmente definido o período entre 2020 e 2024 para análise das tendências climáticas e energéticas.

Entretanto, a infraestrutura desenvolvida posteriormente passou a contemplar uma série histórica ampliada, incluindo dados entre 2016 e 2024.

Para a etapa de Machine Learning, será utilizado preferencialmente o maior período histórico disponível que apresente qualidade e consistência suficientes entre as diferentes fontes de dados.

A utilização de uma série histórica mais extensa permite aumentar a quantidade de observações disponíveis para treinamento, além de possibilitar melhor representação de ciclos sazonais, períodos de maior ou menor disponibilidade hídrica e diferentes comportamentos climáticos e energéticos.

Os dados serão divididos respeitando sua sequência cronológica, separando períodos destinados ao treinamento, validação e teste dos modelos. Essa abordagem evita que informações futuras sejam utilizadas durante o processo de treinamento e permite avaliar de maneira mais realista a capacidade de previsão da solução.

Como estratégia inicial, poderão ser utilizados:

Treinamento: 2016 a 2022
Validação: 2023
Teste: 2024

A definição final desses intervalos poderá ser ajustada de acordo com a disponibilidade, completude e qualidade dos dados integrados.
