# Apresentação Executiva — Consumo Horário de Energia (PJM) e Potencial H₂

## Capa
- Projeto: Previsão e Análise de Consumo Horário — PJM Interconnection
- Extensão: Avaliação de Potencial Operacional para Hidrogênio Verde
- Artefatos principais: EDA, MVP, Qualidade, H₂ e Auditoria

## Sumário
- Contexto e Objetivos
- Dataset e Estrutura
- Qualidade dos Dados
- EDA: Achados Principais
- MVP: Fator de Carga e Padrões
- MVP: Previsão
- Hidrogênio Verde: Potencial
- Governança e Metadados
- Recomendações e Próximos Passos

## Contexto e Objetivos
- Objetivo geral: entender padrões de carga horária e construir análises acionáveis para operação, planejamento e flexibilização.
- Objetivo H₂: estimar potencial de produção em janelas off‑peak com parâmetros operacionais.
- Uso: apoio a decisões (capacidade, deslocamento de carga, rotas off‑peak, avaliação de H₂).

## Dataset e Estrutura
- Fonte: Kaggle/PJM — séries horárias em MW por zonas (AEP, COMED, DAYTON, DEOK, DOM, DUQ, EKPC, FE, NI, PJME, PJMW, PJM_Load).
- Estrutura de pastas:
  - `data/raw/` (CSVs por zona), `data/processed/` (integrados, parquet), `reports/` (MD + figuras), `docs/`, `configs/`, `src/`.
- Metadados:
  - `configs/params.yaml`: zonas e caminhos
  - `data/catalog.yaml`: arquivo/zonas/unidade/frequência/colunas/fonte
  - `data/manifest.json`: hashes/tamanhos (integridade)
- Glossário de siglas em `docs/glossario_projeto.md`.

## Qualidade dos Dados
- CSVs por zona (amostras) sem nulos/duplicatas em `Datetime` (ver `reports/quality_report.md`).
- Dataset integrado (`data/processed/pjm_integrated.csv`) com colunas de zonas parcialmente vazias nas amostras iniciais; `PJM_Load` preenchido.
- Recomendação: revisar integração/joins e coberturas por período; consolidar diretórios duplicados.

## EDA: Achados Principais
- Estatísticas `PJM_Load_MW` (ver `reports/eda_report.md`):
  - Média ≈ 29.766 MW; mediana ≈ 29.655 MW; desvio ≈ 5.850 MW; min 17.461 MW; máx 54.030 MW; skew ≈ 0.558
  - Outliers (IQR): 567 (≈ 1,72%)
- Visualizações:
  - Histogramas: `reports/figures/eda_hist_PJM_Load_MW.png`
  - Correlações: `reports/figures/eda_corr_heatmap.png`

## MVP: Fator de Carga e Padrões
- Fator de carga diário (AEP): `reports/mvp_daily_load_factor_AEP.csv`
  - `fator = média diária / pico diário` (0–1)
  - Dias com menor fator identificam maior “pico‑intensidade” (candidatos a suavização/elasticidade).
- Visualizações:
  - Histogramas: `reports/figures/mvp_hist_AEP.png`, `reports/figures/mvp_hist_PJM_Load.png`
  - Curvas médias por hora (2018): `reports/figures/mvp_hourcurve_AEP_2018.png`, `reports/figures/mvp_hourcurve_PJM_Load_2018.png`
  - Curva média por dia da semana: `reports/figures/mvp_dowcurve_AEP.png`, `reports/figures/mvp_dowcurve_PJM_Load.png`
  - Pico vs média: `reports/figures/mvp_peak_vs_mean_AEP.png`

## MVP: Previsão
- Período de teste: 2018 (AEP)
- Métricas:
  - Baseline (lag 1h): MAE ≈ 415,14 | RMSE ≈ 525,10
  - Regressão Linear (hora, dia_semana, mês, lag1, lag24): MAE ≈ 392,02 | RMSE ≈ 491,75
- Uso: referencial simples para avaliar ganho de modelos e apoiar decisões operacionais.

## Hidrogênio Verde: Potencial Operacional
- Parâmetros (ver `configs/h2_params.yaml`):
  - Capacidade eletrolisador: 10 MW
  - Eficiência: 52 kWh/kg
  - Percentil off‑peak: 25%
  - Fator emissões: 0,0004 kg/kWh
- Sumário (ver `reports/h2_report.md`):
  - Horas off‑peak: 8.226
  - H₂ total estimado: 1.581.923 kg
  - CO₂e por kg estimado: 0,021 kg/kg
- Visual:
  - `reports/figures/h2_potential.png` (carga vs produção horária H₂)

## Governança e Metadados
- Catálogo de dados (`data/catalog.yaml`) e manifesto (`data/manifest.json`) para integridade/reprodutibilidade.
- Relatório de qualidade (`reports/quality_report.md`) e auditoria (`reports/dataset_audit.md`) com recomendações.
- Padrões de nomes e organização documentados (`README.md`, `.trae/documents/*`).

## Recomendações e Próximos Passos
- Estrutura:
  - Consolidar `data/hourly energy consumption` → `data/raw` e remover duplicidades.
  - Particionar parquet integrado por ano/mês e indexar por `Datetime`.
- Metadados:
  - Expandir `catalog.yaml` com `date_range` por arquivo e `quality_checks`; alinhar raiz do `manifest.json`.
- Dados:
  - Revisar integração para preencher zonas no dataset integrado; validar coberturas/joins.
  - Tratar outliers e aplicar caps por percentis conforme necessidade.
- H₂:
  - Integrar meteorologia/feriados; construir KPIs/dashboards; avaliar LCOH e intensidade de carbono.

## Referências de Execução
- EDA: `python eda_report.py`
- MVP: `python mvp_energy.py`
- Qualidade/Manifesto: `python src/quality_checks.py`
- Integração: `python src/data_prep.py`
- H₂: `python src/cli.py`

