# Slide 1 — Contexto e Objetivo
- PJM e AEP: operador regional e zona de carga com histórico horário em MW.
- Objetivo: entender a curva de carga e identificar janelas de suavização para smart energy.
- MVP: diagnóstico inicial de padrões + modelo simples de referência (baseline e linear).

# Slide 2 — Dados e Preparação
- Fonte: Kaggle/PJM; granularidade: horária; período amplo por zona.
- Limpeza: `Datetime` padronizado, duplicidades agregadas por hora.
- Features: calendário (`hora`, `dia_semana`, `mes`, `ano`, `estacao`) e flags `fim_semana`/`dia_util`.
- Referências: `data/raw/*_hourly.csv`, `mvp_energy.py` (`load_series`, `add_time_features`).

# Slide 3 — Curva média por hora (ano de teste)
- Formato típico da curva diária e diferenças sazonais.
- Figura: `reports/figures/mvp_hourcurve_AEP_2018.png`
- Interpretação: horários de pico e vale; candidatos a deslocamento.

# Slide 4 — Curva por dia da semana
- Diferença entre dias úteis e fim de semana; padrão operacional.
- Figura: `reports/figures/mvp_dowcurve_AEP.png`
- Interpretação: menor carga em fim de semana; oportunidades de ajustes operacionais.

# Slide 5 — Fator de Carga e Pico vs Média
- Fator = média diária / pico diário; dias com menor fator são “pico‑intensivos”.
- CSV: `reports/mvp_daily_load_factor_AEP.csv`
- Figura: `reports/figures/mvp_peak_vs_mean_AEP.png`
- Interpretação: dias com maior distância entre pico e média sugerem suavização.

# Slide 6 — Modelos e Sumário Executivo
- Baseline lag‑1 (referência mínima), Linear v1 (lags+calendário), Linear v2 (lags+calendário+fim de semana).
- Tabela (no relatório): MAE/RMSE — baseline vs v1 vs v2.
- Referência: `reports/mvp_report.md` (sumário executivo).

# Slide 7 — Validação Temporal e Resíduos
- CV expanding e rolling com MAE/RMSE por ano (v1 e v2).
- Resíduos:
  - v1: `reports/figures/mvp_resid_hist_AEP.png`, `reports/figures/mvp_resid_hour_AEP.png`
  - v2: `reports/figures/mvp_resid_hist_AEP_v2.png`, `reports/figures/mvp_resid_hour_AEP_v2.png`
- Interpretação: onde o modelo erra mais por hora do dia; se o v2 melhora nos horários críticos.

# Slide 8 — Insights e Próximos Passos
- Insights: horários de pico/vale; dias problemáticos (baixo fator); diferenças dia útil/fim de semana.
- Uso prático: suavização de carga, planejamento, sinalização de preço.
- Próximos passos: modelos mais complexos (GBM/árvore/temporal), incorporar clima/feriados/perfis.
- Referências: `docs/apresentacao_projeto_pjm.md`, `reports/mvp_report.md`.
