# Roteiro de Apresentação — PJM/AEP (MVP Analítico)

## 1. Abertura: contexto e objetivo
- Título: Contexto PJM/AEP e objetivo
- O que falar: PJM é o operador regional de transmissão; AEP é uma das zonas. Vamos entender a curva de carga horária e identificar janelas de suavização.
- Objetivo do MVP: construir um diagnóstico de padrões e um modelo simples como referência para smart energy/elasticidade.

## 2. Dados e preparação (rápido)
- Título: Dados, período e limpeza
- O que falar: Fonte Kaggle/PJM, granularidade horária, período amplo. Limpeza incluiu padronização de `Datetime`, tratamento de duplicidades por hora e criação de variáveis de calendário e flags de fim de semana.
- Referências: `data/raw/*_hourly.csv`, `mvp_energy.py: load_series`, `add_time_features`.

## 3. Padrões operacionais (gráficos‑chave)
- Título: Padrões de operação
- O que falar: Mostrar formato diário da carga, diferença entre dias úteis/fins de semana e comportamento de pico vs média; comentar onde estão picos/vales e oportunidades de deslocamento.
- Figuras:
  - Curva média por hora (ano teste): `reports/figures/mvp_hourcurve_AEP_2018.png`
  - Curva por dia da semana: `reports/figures/mvp_dowcurve_AEP.png`
  - Pico vs média (dispersão): `reports/figures/mvp_peak_vs_mean_AEP.png`
- Complemento: Fator de carga diário (piores dias) em `reports/mvp_daily_load_factor_AEP.csv`.

## 4. Modelos e resultados
- Título: Baseline e Modelos Lineares
- O que falar: Baseline lag‑1 (referência mínima). Linear v1 (lags+calendário) e Linear v2 (lags+calendário+fim de semana). Comparar ganhos vs baseline e efeito do fim de semana.
- Sumário executivo (no relatório): tabela MAE/RMSE de baseline, Linear v1 e Linear v2 em `reports/mvp_report.md`.
- Diagnóstico de resíduos:
  - v1: `reports/figures/mvp_resid_hist_AEP.png`, `reports/figures/mvp_resid_hour_AEP.png`
  - v2: `reports/figures/mvp_resid_hist_AEP_v2.png`, `reports/figures/mvp_resid_hour_AEP_v2.png`
- Validação temporal: expanding/rolling com MAE/RMSE por ano (v1 e v2) descrito no relatório.

## 5. Encerramento: insights e próximos passos
- Título: Insights e próximos passos
- O que falar: Principais achados — horários de pico e vale, dias problemáticos (baixo fator de carga), diferenças fim de semana/dia útil. Uso prático — suavização, planejamento e sinais de preço. Próximos passos técnicos — modelos mais complexos, incorporar clima e perfis de cliente.
- Referências: `docs/apresentacao_projeto_pjm.md` (visão executiva), `reports/mvp_report.md` (detalhes).
