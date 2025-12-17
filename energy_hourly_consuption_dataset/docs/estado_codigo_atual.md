# Estado do Código Atual — Projeto PJM/AEP (MVP Analítico + H₂)

## Visão Geral
- Objetivo: analisar curva de carga horária (EDA, métricas, modelos) e conectar com potencial operacional de H₂ em janelas off‑peak.
- Entregáveis: relatórios Markdown, figuras, CSVs de métricas, dashboard local.
- Linguagem/Deps: Python 3, `pandas`, `numpy`, `matplotlib`, `seaborn` (`requirements.txt`).

## Estrutura de Pastas
- `data/raw`: CSVs originais (ex.: `AEP_hourly.csv`, `PJM_Load_hourly.csv`)
- `data/processed`: dataset integrado (`pjm_integrated.csv`)
- `data/external/meteo`: CSVs de clima (opcional) para join
- `reports`: Relatórios e CSVs de métricas
- `reports/figures`: Figuras geradas (EDA/MVP/H₂)
- `src`: Código modular (qualidade, ingestão, H₂, dashboard, clima)
- `docs`: Documentos de apresentação, glossário, setup

## Principais Módulos e Funções
- MVP de energia: `mvp_energy.py`
  - Ingestão/limpeza: `load_series` em Consumo Horário de Energia/mvp_energy.py:20
  - Features de calendário e feriados: `add_time_features` em Consumo Horário de Energia/mvp_energy.py:39
  - EDA operacional:
    - `plot_histogram` em Consumo Horário de Energia/mvp_energy.py:62
    - `hourly_curve_year` em Consumo Horário de Energia/mvp_energy.py:76
    - `dow_curve` em Consumo Horário de Energia/mvp_energy.py:95
  - Métricas de operação:
    - `daily_load_factor` em Consumo Horário de Energia/mvp_energy.py:131
    - `plot_peak_vs_mean` em Consumo Horário de Energia/mvp_energy.py:147
  - Modelagem:
    - Features e split: `build_features` em Consumo Horário de Energia/mvp_energy.py:162; `split_train_test` em Consumo Horário de Energia/mvp_energy.py:181
    - Regressão linear e baseline: `fit_linear_regression` em Consumo Horário de Energia/mvp_energy.py:199; `baseline_prev` em Consumo Horário de Energia/mvp_energy.py:230
    - v2 com `fim_semana` e `feriado`: `build_features_weekend` em Consumo Horário de Energia/mvp_energy.py:190
    - Validação temporal: `time_series_cv` em Consumo Horário de Energia/mvp_energy.py:205
    - Resíduos: `plot_residuals` em Consumo Horário de Energia/mvp_energy.py:285
    - Comparações:
      - v1 vs v2 por hora: `plot_residuals_model_compare` em Consumo Horário de Energia/mvp_energy.py:380
      - Feriado vs não feriado: `plot_residuals_holiday_comparison` em Consumo Horário de Energia/mvp_energy.py:315
      - Tabelas/ganhos: `hourly_error_table` e `plot_hourly_improvement_bar` em Consumo Horário de Energia/mvp_energy.py:392
  - Relatório: `write_report` em Consumo Horário de Energia/mvp_energy.py:393
  - Pipeline: `main` em Consumo Horário de Energia/mvp_energy.py:502
- Qualidade de dados: `src/quality_checks.py`
  - Manifesto: `write_manifest` em Consumo Horário de Energia/src/quality_checks.py:36
  - Relatório de qualidade: `write_quality_report` em Consumo Horário de Energia/src/quality_checks.py:53
  - Execução: `main` em Consumo Horário de Energia/src/quality_checks.py:73
- Integração de séries: `src/data_prep.py`
  - Carregar e integrar por `Datetime`: `load_raw`/`integrate` em Consumo Horário de Energia/src/data_prep.py:4,20
  - Salvar integrado: `write_csv` em Consumo Horário de Energia/src/data_prep.py:29
  - Execução: `main` em Consumo Horário de Energia/src/data_prep.py:36
- Pipeline H₂: `src/cli.py`
  - Ingestão e seleção de carga: `load_integrated` / `select_load` em Consumo Horário de Energia/src/h2_ingest.py:4,17
  - Features e flags off‑peak: `add_calendar`/`compute_offpeak_flags` em Consumo Horário de Energia/src/h2_features.py:4,11
  - Estimativa H₂ e relatório: `estimate_h2_potential` / `write_report` em Consumo Horário de Energia/src/h2_features.py:18 e Consumo Horário de Energia/src/h2_reporting.py:17
  - Execução: `main` em Consumo Horário de Energia/src/cli.py:13
- Dashboard local: `src/dashboard_server.py`
  - Handler e renderização: `DashboardHandler.do_GET` em Consumo Horário de Energia/src/dashboard_server.py:98
  - Lista de figuras EDA/MVP: `list_images` em Consumo Horário de Energia/src/dashboard_server.py:91
  - Servidor: `run_server` em Consumo Horário de Energia/src/dashboard_server.py:161
- Clima (conector e fetch)
  - Conector: `src/meteo_ingest.py` (carrega diretório e join por `Datetime`)
    - `load_meteo_dir` em Consumo Horário de Energia/src/meteo_ingest.py:13
    - `join_meteo` em Consumo Horário de Energia/src/meteo_ingest.py:28
  - Fetch Open‑Meteo: `src/meteo_fetch_openmeteo.py`
    - `fetch_open_meteo` em Consumo Horário de Energia/src/meteo_fetch_openmeteo.py:8
    - `main` e `save_csv` em Consumo Horário de Energia/src/meteo_fetch_openmeteo.py:45,38
  - Modelagem com clima: `src/train_weather_model.py`
    - Comparação de modelo base vs modelo com variáveis climáticas.
    - Gera `reports/figures/weather_model_comparison.png` e métricas.

## Funcionalidades Recentes
- Robustez na ingestão: agregação de duplicidades em `load_series` (`agg` configurável).
- Flags operacionais: `fim_semana`, `dia_util` e `feriado` adicionadas às features e ao modelo v2.
- Validação temporal: expanding/rolling adicionada para v1 e v2.
- Diagnóstico: histogramas e erro por hora; comparações v1 vs v2; feriado vs não feriado; tabela e gráfico de ganhos por hora.
- Clima: 
  - Conector genérico com join por `Datetime`.
  - Fetch Open-Meteo (Archive API) para dados históricos.
  - Modelo comparativo demonstrando ganho de performance (~4.6% de redução no MAE em 2018).

## Saídas Geradas
- Relatório MVP: `reports/mvp_report.md` (sumário executivo, EDA, métricas, modelos, CV, resíduos)
- Relatório Clima: `reports/weather_model_report.md` (comparação base vs weather)
- Figuras: `reports/figures/*` (EDA/MVP/resíduos/comparações)
  - Exemplos: `mvp_hist_AEP.png`, `weather_model_comparison.png`
- CSVs:
  - Fator de carga diário: `reports/mvp_daily_load_factor_AEP.csv`
  - Comparação de erro por hora v1 vs v2: `reports/mvp_hourly_error_compare_AEP.csv`
- H₂: `reports/h2_report.md` e `reports/figures/h2_potential.png`
- Qualidade: `reports/quality_report.md`, `data/manifest.json`

## Como Executar
- MVP energia: `python mvp_energy.py`
- Qualidade: `python src/quality_checks.py`
- Integração: `python src/data_prep.py`
- H₂: `python src/cli.py`
- Dashboard: `python src/dashboard_server.py` e abrir `http://localhost:8000/`
- Figuras estáticas: `python -m http.server 8010` em `reports/figures` e abrir `http://localhost:8010/`
- Clima:
  - Baixar: `python src/meteo_fetch_openmeteo.py 39.9612 -82.9988 2016-01-01 2018-12-31`
  - Integrar: `python src/data_prep.py` (automático se CSVs existirem em `data/external/meteo`)
  - Treinar/Avaliar: `python src/train_weather_model.py`

## Próximos Passos
- Testar modelos não lineares (XGBoost/LightGBM) usando o dataset enriquecido com clima.
- Organizar dashboard com seções separadas “Carga (MVP)”, “H₂” e “Clima”.
