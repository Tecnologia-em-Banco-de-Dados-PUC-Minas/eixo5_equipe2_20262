**ETAPA 1**  

### TÍTULO DO PROJETO:  

Análise Integrada de Dados Climáticos e Elétricos Utilizando Big Data Analytics   
 

**1\. Motivação da Escolha do Tema**

Como grupo, decidimos focar no tema **Energia & Clima** por entendermos que ele representa um dos cenários mais aderentes e desafiadores para a aplicação real dos conceitos de **Big Data Analytics**. Nossa escolha foi pautada em três pilares fundamentais:

**1.1 Aderência aos “Vs” do Big Data (Volume, Velocidade e Variedade)**

O setor elétrico brasileiro e o monitoramento climático geram um fluxo contínuo e massivo de dados. Ao utilizarmos fontes públicas governamentais, como o Operador Nacional do Sistema Elétrico (ONS) e o Instituto Nacional de Meteorologia (INMET), teremos acesso a séries temporais de alta frequência, com dados horários ou próximos do tempo real.

Isso nos permite trabalhar com um volume substancial de dados brutos em diferentes formatos, como JSON, CSV e APIs REST, exigindo o desenho de uma arquitetura de ingestão, tratamento e processamento de dados robusta.

**1.2. Relevância Socioeconômica e Prática**

A matriz elétrica brasileira é fortemente dependente de fontes renováveis, como hidrelétrica, eólica e solar, o que a torna intrinsecamente sensível às variações climáticas.

Compreender a correlação entre variáveis como velocidade do vento, incidência de radiação solar, índices pluviométricos e temperatura com a curva de geração e demanda de energia não é apenas um exercício acadêmico, mas uma necessidade estratégica para o planejamento e a segurança energética do país.

**1.3. Desafio Técnico de Integração de Dados**

O cruzamento de dados climáticos e elétricos apresenta desafios relevantes de engenharia de dados, especialmente devido às diferenças de granularidade temporal e espacial entre as fontes.

Por exemplo, dados provenientes de estações meteorológicas precisam ser correlacionados com a localização geográfica de usinas e centros de carga, exigindo processos de padronização, modelagem e integração de dados.

Resolver essas complexidades demonstra domínio de práticas fundamentais de engenharia e análise de dados, reforçando o caráter aplicado do projeto.

**2\. Contexto do Problema e Cliente**

O presente projeto considera como cliente fictício o Operador Nacional do Sistema Elétrico (ONS), entidade responsável pela coordenação e controle da operação das instalações de geração e transmissão de energia elétrica no Brasil. Sua atuação é fundamental para garantir o equilíbrio entre a oferta e a demanda de energia, assegurando a estabilidade e a confiabilidade do sistema elétrico nacional.

Um dos principais desafios enfrentados pelo ONS está relacionado à gestão eficiente dos recursos hídricos utilizados na geração hidrelétrica, que representa parcela significativa da matriz elétrica brasileira. A operação dos reservatórios exige decisões contínuas sobre armazenamento, liberação e aproveitamento da água, de forma a maximizar a geração de energia e minimizar desperdícios, ao mesmo tempo em que se preserva a segurança do sistema.

Nesse contexto, a análise de dados hidrológicos e operacionais torna-se essencial para apoiar a tomada de decisão. A compreensão do comportamento dos reservatórios, incluindo níveis de armazenamento, vazões de entrada e saída, padrões de operação das usinas e fluxos entre bacias, permite avaliar a eficiência do uso da água e identificar oportunidades de melhoria na gestão do sistema. Além disso, a identificação de gargalos operacionais e padrões de desempenho contribui para um planejamento mais assertivo e para a otimização da geração hidrelétrica.

Dessa forma, o projeto propõe responder à seguinte questão central de análise: “Como o desempenho operacional dos reservatórios e usinas hidrelétricas impactam a eficiência da geração de energia no sistema elétrico brasileiro, e de que forma a análise desses dados pode apoiar decisões mais eficazes na gestão dos recursos hídricos?”

A partir dessa perspectiva, o desenvolvimento de um sistema analítico baseado em dados permitirá avaliar a criticidade dos subsistemas em termos de armazenamento, analisar o balanço hídrico dos reservatórios, mensurar a eficiência da geração a partir do uso da água, identificar períodos de maior aporte hídrico e mapear a dependência entre bacias por meio da transferência de vazões. Adicionalmente, será possível estabelecer comparações de desempenho entre usinas, construir indicadores de criticidade baseados em volume e afluência, identificar gargalos operacionais e agrupar reservatórios de acordo com seus padrões de comportamento, contribuindo para uma visão integrada e orientada à performance do sistema hidrelétrico nacional.

**3\. Objetivo Geral**

Desenvolver um sistema analítico baseado em dados capaz de integrar informações climáticas e energéticas, com o objetivo de analisar como variáveis ambientais influenciam a geração de energia e a demanda elétrica no sistema brasileiro, apoiando a tomada de decisão operacional no contexto do Operador Nacional do Sistema Elétrico (ONS).

**3.1. Objetivos Específicos**

* Realizar a coleta e integração de dados provenientes de fontes públicas, incluindo dados de geração e carga do sistema elétrico e dados climáticos, garantindo consistência temporal e estrutural entre as bases.  
* Tratar, padronizar e organizar os dados em um ambiente estruturado, permitindo sua utilização para análise e construção de indicadores.  
* Desenvolver indicadores analíticos que permitam avaliar a relação entre variáveis climáticas (como temperatura, velocidade do vento, radiação solar e precipitação) e variáveis do sistema elétrico (como geração por fonte e demanda de energia).  
* Construir um modelo de dados que viabilize a exploração analítica das informações por meio de consultas e agregações.  
* Desenvolver dashboards interativos que permitam a visualização dos dados e dos indicadores construídos, facilitando a interpretação dos resultados.  
* Apoiar a compreensão dos impactos das variáveis climáticas na operação do sistema elétrico, contribuindo para a tomada de decisão baseada em dados.

**4\. Definição das Métricas e Indicadores de Análise**

Para viabilizar a análise proposta, foram definidas métricas provenientes de duas categorias principais: dados elétricos e dados climáticos. As métricas elétricas incluem a geração total de energia (MW), a geração por fonte — especialmente hidrelétrica, eólica e solar — e a carga do sistema elétrico, que representa a demanda total de energia em determinado período.

No campo climático, serão utilizadas métricas como temperatura média, velocidade do vento, radiação solar e precipitação (chuva), por serem variáveis diretamente relacionadas ao comportamento das principais fontes renováveis da matriz energética brasileira.

A partir dessas métricas, serão construídos indicadores analíticos que permitam compreender a relação entre condições climáticas e geração ou demanda de energia. Entre os principais indicadores previstos estão: a correlação entre velocidade do vento e geração eólica, o impacto da radiação solar na geração fotovoltaica, a relação entre precipitação e geração hidrelétrica e a influência da temperatura na demanda elétrica. Esses indicadores permitirão identificar padrões, dependências e possíveis tendências entre variáveis ambientais e energéticas. 

**5\. Recorte Temporal da Análise**

O estudo adotará como recorte temporal o período entre 2020 e 2024, considerando tanto a disponibilidade de dados públicos nas plataformas institucionais quanto a relevância de um período recente para análise de tendências climáticas e energéticas.

Esse intervalo de cinco anos possibilita trabalhar com um volume significativo de dados em séries temporais, permitindo observar padrões sazonais, variações anuais e eventuais anomalias climáticas que possam impactar a geração e o consumo de energia. Além disso, trata-se de um período marcado pela expansão das fontes renováveis, especialmente da geração solar e eólica no Brasil, tornando a análise ainda mais relevante para compreender a crescente dependência da matriz elétrica em relação às condições climáticas.Texto
