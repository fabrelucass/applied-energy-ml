# Previsão de Consumo Horário de Energia (PJM)

Este projeto realiza análise exploratória e modelagem de séries temporais para prever o consumo horário de energia elétrica em diferentes zonas da PJM Interconnection, utilizando o dataset público "Hourly Energy Consumption" do Kaggle.

## 1. Objetivo do projeto
- Prever o consumo de energia (MW) das empresas/regiões da PJM para horizontes futuros (ex.: próximos 12 meses).
- Explorar padrões sazonais, diários e anuais de carga, bem como correlações entre as zonas (AEP, COMED, DAYTON, DEOK, DOM, DUQ, EKPC, FE, NI, PJM_Load etc.).

## 2. Sobre o dataset
- Fonte: Kaggle – Hourly Energy Consumption (autor: robikscube).
- Origem dos dados: site oficial da PJM Interconnection (operador regional de transmissão dos EUA).
- Unidade: Megawatts (MW), em frequência horária, com mais de 10 anos de histórico para várias zonas.
- Principais arquivos por zona e agregado (exemplos): `AEP_hourly.csv`, `COMED_hourly.csv`, `DAYTON_hourly.csv`, `DEOK_hourly.csv`, `DOM_hourly.csv`, `DUQ_hourly.csv`, `EKPC_hourly.csv`, `FE_hourly.csv`, `NI_hourly.csv`, `PJM_Load_hourly.csv`.

### Significados das siglas (Tabela rápida)
- AEP: American Electric Power — Vários estados na zona AEP (PJM)
- COMED: Commonwealth Edison Company — Norte de Illinois (Chicago)
- DAYTON (DAY): Dayton Power & Light — Região de Dayton, Ohio
- DEOK: Duke Energy Ohio & Kentucky — Zona Ohio/Kentucky
- DOM: Dominion Energy — Principalmente Virgínia e arredores
- DUQ: Duquesne Light — Região de Pittsburgh, PA
- EKPC: East Kentucky Power Cooperative — Leste de Kentucky
- FE: FirstEnergy (ATSI e afins) — Utilities em OH, PA e região
- NI (NIPSCO): Northern Indiana Public Service — Norte de Indiana
- PJM_Load: Carga total PJM — Sistema agregado da PJM

## 3. Estrutura do repositório
- `eda_report.py` — script de EDA automática e geração de relatório/figuras
- `eda_output/` — relatório e figuras geradas pela EDA atual
- (Opcional) `data/raw/` — arquivos CSV originais baixados do Kaggle
- (Opcional) `data/processed/` — dados tratados e integrados para modelagem
- (Opcional) `notebooks/`
  - `01_eda.ipynb` — análise exploratória, histogramas, matriz de correlação
  - `02_feature_engineering.ipynb` — criação de features temporais e agregações
  - `03_modelling.ipynb` — treinamento e avaliação dos modelos
- (Opcional) `src/`
  - `data_prep.py` — funções de limpeza e transformação
  - `features.py` — criação de variáveis de calendário e lags
  - `models.py` — definição, treino e previsão dos modelos
- (Opcional) `reports/figures/` — figuras consolidadas de relatórios

## 4. Fluxo metodológico
- Entendimento do negócio
  - Uso das previsões para apoiar planejamento de capacidade, investimentos em geração/transmissão e gestão de demanda.
- Entendimento e preparação dos dados
  - Tratamento de datas, fusos, valores faltantes, outliers e integração entre séries das diferentes zonas.
- Análise exploratória (EDA)
  - Histogramas por zona e correlação entre cargas.
  - Geração automática via `eda_report.py` com saída em `eda_output/`.
- Modelagem
  - Modelos de regressão e séries temporais (baseline, regressão linear, modelos em árvore/boosting, etc.).
- Avaliação
  - Métricas como MAE, RMSE e MAPE, com foco na interpretação em MW e impacto de negócio.
- Implantação (opcional)
  - Script ou API para gerar previsões a partir de novos dados de data/hora.

## 5. Como reproduzir
1. Criar e ativar um ambiente virtual (opcional).
2. Instalar dependências:
   - `pip install -r requirements.txt`
3. Garantir que os CSVs estejam acessíveis:
   - (Opção A) baixar do Kaggle e colocar em `data/raw/`.
   - (Opção B) usar os arquivos já presentes na pasta atual.
4. Gerar a EDA automática:
   - `python eda_report.py` (usa `pjm_hourly_est.csv` por padrão)
   - ou `python eda_report.py <arquivo.csv>` para outro CSV.
5. Abrir o relatório:
   - `eda_output/eda_report.md` (lista das figuras geradas: `eda_hist_*.png`, `eda_corr_heatmap.png`).

## 6. Licença e uso dos dados
- Os dados originais da PJM no Kaggle estão sob licença informada na própria página do dataset e vêm do site oficial da PJM, em MW horários.
- Este projeto respeita propriedade intelectual e direitos autorais, utilizando os dados apenas para fins educacionais e de pesquisa, sem reproduzir conteúdo protegido de terceiros.

