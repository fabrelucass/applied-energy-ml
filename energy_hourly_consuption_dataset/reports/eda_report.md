# Relatório de Análise Exploratória

Arquivo analisado: `PJM_Load_hourly.csv`
Conteúdo: Hourly Energy Consumption

## 1. Estrutura dos dados
Total de registros: 32896
Total de colunas: 2
Colunas e tipos:
- Datetime: data
- PJM_Load_MW: numerico

## 1.1 Significados das siglas
Tabela rápida:

## 2. Qualidade dos dados
Valores ausentes por coluna:
- Datetime: 0 (0.00%)
- PJM_Load_MW: 0 (0.00%)

Estatísticas básicas (numéricas):
- PJM_Load_MW: média 29766.427407587547, mediana 29655.0, desvio 5849.76995358659, min 17461.0, max 54030.0, skew 0.5575442671090831

Outliers (IQR):
- PJM_Load_MW: 567 (1.72%)

Cardinalidade (categóricas):

## 3. Duplicatas
Registros duplicados completos: 0 (0.00%)

## 3.1 Exemplos de dados problemáticos

## 4. Visualizações
Histogramas (numéricos):
- `eda_hist_PJM_Load_MW.png`

## 5. Problemas e recomendações
Problemas identificados:
- Nenhum problema relevante identificado

Recomendações:
- Prosseguir com modelagem ou análises avançadas