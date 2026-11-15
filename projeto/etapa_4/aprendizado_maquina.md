# 4. ETAPA 4 — MODELAGEM E PREVISÃO DE CARGA ELÉTRICA

Esta etapa apresenta a construção, o treinamento e a comparação técnica dos modelos de aprendizado de máquina aplicados à previsão de carga elétrica no Sistema Interligado Nacional (SIN), organizados em duas frentes complementares:

1. **Parte I — Modelo Baseline Mensal (`modelo2.py`):** primeira abordagem por subsistema na escala mensal, utilizando tendência temporal e sazonalidade de calendário (sem variáveis climáticas).
2. **Parte II — Comparação de Modelos na Base Diária com Clima (`comparacao_modelos/`):** evolução do experimento na granularidade diária integrando dados meteorológicos do INMET e histórico recente da carga (*lags*), comparando **Regressão Linear**, **Random Forest** e **Gradient Boosting**.

---

# PARTE I — MODELO INICIAL MENSAL (REGRESSÃO LINEAR)

**Código em:** [`modelo2.py`](modelo2.py)

## 1.1. Base de dados

A modelagem utilizou os dados da tabela `gold_fato_carga`, consultada no Amazon Athena. A base contempla o período de janeiro de 2016 a dezembro de 2024, com 13.152 registros diários distribuídos entre os quatro subsistemas.

Para a previsão, os dados foram agregados mensalmente pela média da carga (`val_cargaenergiamwmed`), resultando em 432 registros, sendo 108 para cada subsistema.

| Subsistema           | Carga média (MWmed) |
| -------------------- | ------------------: |
| Norte                |            6.025,39 |
| Nordeste             |           11.018,78 |
| Sudeste/Centro-Oeste |           38.537,02 |
| Sul                  |           11.691,99 |

## 1.2. Análise exploratória

A análise histórica mostrou diferenças no comportamento da carga entre os subsistemas, tanto em relação à escala quanto à variação ao longo dos meses.

Também foram identificados padrões sazonais distintos:

| Subsistema           | Maior média | Menor média |
| -------------------- | ----------- | ----------- |
| Nordeste             | Novembro    | Julho       |
| Norte                | Setembro    | Janeiro     |
| Sudeste/Centro-Oeste | Março       | Julho       |
| Sul                  | Fevereiro   | Maio        |

### Evolução histórica da carga

![Evolução da carga do Nordeste](imagens/evolucao_nordeste.png)
![Evolução da carga do Norte](imagens/evolucao_norte.png)
![Evolução da carga do Sudeste/Centro-Oeste](imagens/evolucao_sudeste_centro_oeste.png)
![Evolução da carga do Sul](imagens/evolucao_sul.png)

### Sazonalidade mensal

![Sazonalidade da carga do Nordeste](imagens/sazonalidade_nordeste.png)
![Sazonalidade da carga do Norte](imagens/sazonalidade_norte.png)
![Sazonalidade da carga do Sudeste/Centro-Oeste](imagens/sazonalidade_sudeste_centro_oeste.png)
![Sazonalidade da carga do Sul](imagens/sazonalidade_sul.png)

## 1.3. Modelo utilizado

Foi escolhida uma regressão linear com tendência temporal e sazonalidade mensal, aplicada individualmente a cada subsistema.

O modelo considera duas variáveis principais:

- **Tendência:** representa a evolução da carga ao longo do tempo.
- **Sazonalidade:** utiliza variáveis dummy para representar os meses do ano.

De forma simplificada, o modelo estima a carga a partir da tendência temporal e dos efeitos associados a cada mês.

As variáveis climáticas disponíveis na base não foram incluídas nesta primeira versão, ficando implementadas na Parte II desta etapa.

## 1.4. Treinamento e avaliação

A divisão dos dados respeitou a ordem cronológica:

| Etapa       | Período     |
| ----------- | ----------- |
| Treinamento | 2016 a 2022 |
| Teste       | 2023 a 2024 |
| Previsão    | 2025        |

Para avaliar o desempenho, foram utilizadas as métricas MAE, RMSE e MAPE. Também foi realizada uma comparação com um modelo de referência (*baseline*), que utiliza a carga observada no mesmo mês do ano anterior.

| Subsistema           | MAPE Regressão | MAPE Baseline |
| -------------------- | -------------: | ------------: |
| Nordeste             |          8,56% |         7,66% |
| Norte                |         16,09% |        10,83% |
| Sudeste/Centro-Oeste |          7,47% |         6,82% |
| Sul                  |          7,09% |         8,09% |

A regressão apresentou resultado melhor que o baseline apenas no subsistema Sul. Nos demais, o modelo de referência obteve menor erro percentual.

O Norte apresentou o maior erro relativo, enquanto o Sul teve o melhor resultado da regressão.

## 1.5. Previsão para 2025

Após a avaliação, o modelo foi ajustado novamente utilizando todo o histórico de 2016 a 2024, gerando previsões mensais para 2025.

Como exemplo, as estimativas para o subsistema Nordeste foram:

| Mês       | Previsão (MWmed) |
| --------- | ---------------: |
| Janeiro   |        12.812,85 |
| Fevereiro |        12.975,56 |
| Março     |        12.986,21 |
| Abril     |        12.626,26 |
| Maio      |        12.577,04 |
| Junho     |        12.210,47 |
| Julho     |        12.155,12 |
| Agosto    |        12.406,14 |
| Setembro  |        12.689,75 |
| Outubro   |        13.255,08 |
| Novembro  |        13.302,38 |
| Dezembro  |        13.231,01 |

## 1.6. Arquivos e resultados visuais do modelo mensal (`modelo2.py`)

O principal código desta primeira entrega é o [`modelo2.py`](modelo2.py), responsável pela consulta, preparação mensal, treinamento, avaliação e geração das previsões.

| Arquivo | Descrição |
|---|---|
| [`modelo2.py`](modelo2.py) | Script principal da modelagem mensal |
| `metricas_modelo2.csv` | Métricas de avaliação dos modelos mensais |
| `previsoes_teste_modelo2.csv` | Valores reais e previstos no período de teste |
| `previsao_2025_modelo2.csv` | Previsões mensais para 2025 |

Foram utilizadas as bibliotecas Python `awswrangler`, `pandas`, `numpy` e `matplotlib`, além do Amazon Athena para consulta aos dados.

### Resultados visuais do modelo mensal (`modelo2.py`)

![Resultados Nordeste](imagens/resultado%20nordeste.png)
![Resultados Norte](imagens/resultado%20norte.png)
![Resultados Sudeste/Centro-Oeste](imagens/resultado%20sudeste_centro-oeste.png)
![Resultados Sul](imagens/resultado%20sul.png)

---

# PARTE II — COMPARAÇÃO DE ALGORITMOS NA BASE DIÁRIA COM CLIMA E DEFASAGENS

**Pasta dos códigos e resultados:** [`comparacao_modelos/`](comparacao_modelos/README.md)

Para superar as limitações observadas na abordagem mensal sem clima e atender às hipóteses `H1`, `H3`, `H4` e `H5` definidas na Etapa 1, os algoritmos foram implementados na **granularidade diária**, unindo carga elétrica, variáveis meteorológicas e histórico recente da demanda.

## 2.1. Preparação da base diária e atributos (`preparacao.py`)

O módulo [`comparacao_modelos/preparacao.py`](comparacao_modelos/preparacao.py) executa a extração integrada diretamente na camada Gold do Amazon Athena (`db_energia_clima_puc`), cruzando `gold_fato_carga` (ONS), `gold_fato_clima` (INMET) e `gold_dim_localizacao` (IBGE) conforme o mapeamento elétrico oficial dos quatro subsistemas (`SE`, `S`, `NE`, `N`) entre **2016 e 2024** (`13.152` registros diários).

Durante a extração, registros anômalos de sensores meteorológicos são filtrados em SQL (por exemplo, temperaturas médias entre `-10 °C` e `50 °C` e radiação global entre `0` e `4.500 kJ/m²`). Em seguida, são construídos os grupos de variáveis de entrada, respeitando estritamente a ordem cronológica por subsistema (sem vazamento de dados futuros):

- **Variáveis climáticas (INMET):** `temp_max`, `temp_media`, `temp_min`, `precipitacao_total`, `radiacao_global`, `vento_vel_media`, além de `temp_media_lag_1` (temperatura média do dia anterior) e `temp_media_3d` (média móvel dos últimos 3 dias).
- **Variáveis de calendário e estrutura:** `id_subsistema`, `dia_semana`, `mes`, `dia_ano`, `tendencia` (dias desde `2016-01-01`) e `feriado` (incluindo feriados nacionais e pontos facultativos como Carnaval e Corpus Christi via biblioteca `holidays`).
- **Defasagens recentes da carga (*lags*):** `carga_lag_1` (carga do dia anterior), `carga_lag_7` (mesmo dia da semana anterior) e `carga_media_7d` (média móvel dos 7 dias anteriores).

## 2.2. Divisão cronológica e pré-processamento sem vazamento

Seguindo o recorte experimental definido na Etapa 1, os dados diários foram divididos em ordem estritamente temporal:

| Etapa | Período | Quantidade de Registros | Finalidade |
| :--- | :--- | :---: | :--- |
| **Treino inicial** | `2016` a `2022` | `10.200` | Ajuste inicial dos modelos na busca em grade |
| **Validação** | `2023` | `1.460` | Escolha dos melhores hiperparâmetros sem tocar em `2024` |
| **Retreinamento** | `2016` a `2023` | `11.660` *(c/ lags)* / `11.688` *(s/ lags)* | Incorporar o comportamento mais recente antes da avaliação final |
| **Teste final (*holdout*)** | `2024` | `1.464` | Avaliação imparcial de desempenho nos 4 subsistemas |

Os pré-processadores (`SimpleImputer` pela mediana, `StandardScaler` para a Regressão Linear e `OrdinalEncoder`/`OneHotEncoder`) foram encapsulados em `Pipeline` do `scikit-learn`, garantindo ajuste exclusivo nos dados de treino. Para modelos em árvore e na variante linear com defasagens, utilizou-se transformação logarítmica no alvo (`TransformedTargetRegressor` com `np.log`/`np.exp`) a fim de equilibrar as diferentes ordens de grandeza entre subsistemas (`SE` ≈ `45.000 MWmed` vs. `N` ≈ `7.500 MWmed`).

## 2.3. Algoritmos comparados e hiperparâmetros selecionados

1. **[`01_regressao_linear.py`](comparacao_modelos/01_regressao_linear.py) — Regressão Linear Diária (com clima):**
   - Modelo linear de referência usando clima e calendário na base diária (sem *lags*), permitindo avaliar o ganho dos modelos baseados em árvores sobre o mesmo conjunto de atributos climáticos.
   - No comparativo final, avaliou-se também a variante **Regressão Linear + Defasagens (`log-log`)**, na qual os *lags* da carga entram igualmente em escala logarítmica.
2. **[`02_gradient_boosting.py`](comparacao_modelos/02_gradient_boosting.py) — Gradient Boosting (`HistGradientBoostingRegressor`):**
   - Algoritmo de conjunto (*ensemble*) baseado em árvores de decisão sequenciais, em que cada nova árvore ajusta os erros residuais das anteriores. Trata nativamente valores ausentes de estações do INMET nos dias sem medição.
   - **Melhores hiperparâmetros na validação (`2023`, `MAPE = 3,57%`):** `learning_rate = 0.03`, `max_iter = 400`, `max_leaf_nodes = 15`, `min_samples_leaf = 10`.
3. **[`03_random_forest.py`](comparacao_modelos/03_random_forest.py) — Random Forest (`RandomForestRegressor`):**
   - Terceiro algoritmo avaliado pela equipe: conjunto paralelo (*bagging*) com centenas de árvores de decisão treinadas sobre subamostras aleatórias dos dados e dos atributos, combinadas por média.
   - **Melhores hiperparâmetros na validação (`2023`, `MAPE = 3,19%`):** `n_estimators = 400`, `max_features = 0.7`, `min_samples_leaf = 5`.
4. **Modelo de Referência Semanal (`carga_lag_7`):**
   - Regra simples que projeta para o dia atual exatamente a carga registrada sete dias antes.

> **Observação sobre dias pós-feriado na defasagem semanal (mapeada para a Etapa 6):** na inspeção dos desvios de janeiro de `2024`, identificou-se que na segunda-feira **`08/01/2024`** (`Carga real = 47,1 mil MWmed`, `Temp. máxima = 31,6 °C`) a referência `carga_lag_7` apontou para **`01/01/2024`** (`35,1 mil MWmed`, feriado de Ano-Novo), criando uma defasagem abrupta de `+12,0 mil MWmed`. Com isso, fica registrada como **otimização para a Etapa 6** a sinalização ou filtragem de dias úteis cuja semana anterior (`t-7`) tenha sido feriado (`feriado_lag_7`).

## 2.4. Comparação global e seleção do algoritmo vencedor (teste de 2024)

Para identificar qual algoritmo oferece o melhor equilíbrio entre acurácia e generalização, compararam-se todas as abordagens exatamente sobre os `1.464` dias inéditos de `2024` utilizando:

- **MAE (*Mean Absolute Error*, em MWmed):** erro médio absoluto diário;
- **RMSE (*Root Mean Squared Error*, em MWmed):** raiz do erro quadrático médio (mais sensível a desvios elevados);
- **R² (Coeficiente de Determinação):** fração da variabilidade explicada pelo modelo (até `1,00`);
- **MAPE (*Mean Absolute Percentage Error*, em %):** erro médio relativo em porcentagem da carga observada.

| Modelo | MAE (MWmed) | RMSE (MWmed) | R² | MAPE (%) |
| :--- | ---: | ---: | ---: | ---: |
| **Gradient Boosting (`HistGradientBoosting`)** | **424,74** | **691,18** | **0,9978** | **2,20%** |
| **Regressão Linear + Defasagens (`log-log`)** | 499,06 | 769,97 | 0,9972 | **2,77%** |
| **Random Forest (`RandomForestRegressor`)** | 577,26 | 908,39 | 0,9961 | **3,09%** |
| Modelo de Referência Semanal (`carga_lag_7`) | 961,80 | 1.684,20 | 0,9867 | **4,48%** |
| Regressão Linear Diária (clima e calendário, sem defasagens) | 1.793,38 | 2.899,57 | 0,9607 | **8,19%** |

![Comparação global de MAPE entre os modelos em 2024](comparacao_modelos/resultados/comparacao_mape.png)

O **Gradient Boosting** obteve o menor erro em todas as métricas (`MAPE = 2,20%`, `MAE = 424,74 MWmed`, `RMSE = 691,18 MWmed`, `R² = 0,9978`) e foi selecionado como modelo principal para a etapa seguinte.

A análise detalhada dos parâmetros, do impacto das variáveis de entrada, do comportamento regional nos quatro subsistemas e das descobertas climáticas/operacionais é apresentada na [Etapa 5 — Análise dos Resultados](../etapa_5/analise_resultados.md).
