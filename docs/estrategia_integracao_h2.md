# Estratégia de Integração — Sistema de Energia Renovável com Produção de Hidrogênio

## Objetivo
- Integrar dados de demanda (PJM/AEP), clima e renováveis para prever carga e otimizar a alocação entre rede e produção de H₂ verde.
- Entrega um MVP em duas fases com modelos, análises e dashboards reproduzíveis.

## MVP Fase 1 — Implementação Básica
- Dados de entrada:
  - AEP/PJM_Load (demanda histórica horária) — `data/raw/*_hourly.csv`
  - Ohio Weather (clima histórico horário) — via `src/meteo_fetch_openmeteo.py` e `src/meteo_ingest.py`
- Pipeline:
  - Ingestão e limpeza de carga: `Consumo Horário de Energia/mvp_energy.py:20`
  - Features de calendário e feriado: `Consumo Horário de Energia/mvp_energy.py:39`
  - Ingestão de clima (Open‑Meteo) e join por `Datetime`: `src/meteo_fetch_openmeteo.py:8`, `src/meteo_ingest.py:13,28`
- Modelo preditivo:
  - Relação clima → demanda energética
  - Linear baseline (lags+calendário) e extensão com flags (`fim_semana`, `feriado`): `Consumo Horário de Energia/mvp_energy.py:162,190,199`
  - Validação temporal expanding/rolling: `Consumo Horário de Energia/mvp_energy.py:205`
- Saídas:
  - Relatório MVP: `Consumo Horário de Energia/reports/mvp_report.md`
  - Figuras EDA/MVP: `Consumo Horário de Energia/reports/figures/*`
  - Dashboard local: `src/dashboard_server.py:161` (home em `http://localhost:8000/`)

## MVP Fase 2 — Integração de Hidrogênio Verde
- Dados adicionais:
  - Irradiância solar/GHI e variáveis meteo renováveis — `data/external/meteo/*.csv`
  - Renewable Hydrogen Production Dataset — `renewable_hydrogen_dataset/renewable_hydrogen_dataset.csv`
- Pipeline H₂:
  - Ingestão e seleção de carga integrada: `Consumo Horário de Energia/src/h2_ingest.py:4,17`
  - Flags off‑peak e parâmetros operacionais: `Consumo Horário de Energia/src/h2_features.py:11`
  - Estimativa de produção de H₂ e relatório: `Consumo Horário de Energia/src/h2_features.py:18`, `Consumo Horário de Energia/src/h2_reporting.py:17`
- Modelo avançado:
  - Relação clima → demanda
  - Excesso de renováveis → produção de H₂
  - Otimização da alocação rede vs H₂ (alvo econômico/operacional)
- Saídas:
  - Relatório H₂: `Consumo Horário de Energia/reports/h2_report.md`
  - Figura potencial H₂: `Consumo Horário de Energia/reports/figures/h2_potential.png`

## Análises Recomendadas
- Mapeamento de potencial:
  - Identificar regiões/cidades com maior potencial H₂ cruzando PJM e dataset H₂
  - Georreferenciar pontos do dataset H₂ e filtrar área PJM
- Correlações energéticas:
  - Relação irradiância vs demanda
  - Cenários de armazenamento via H₂, usando “heating/cooling degree hours” e GHI
- Simulações de produção:
  - Capacidade de H₂ em baixa demanda; dimensionamento para cobrir picos
  - Curvas de operação e restrições (potência, eficiência, janelas off‑peak)
- Análise econômica:
  - Custos H₂ (kg/dia) vs custo de energia de pico
  - ROI por região; sazonalidade e sinais de preço

## Requisitos Técnicos
- Pipelines de dados:
  - Integração por `Datetime`; catálogo/manifesto e qualidade (`Consumo Horário de Energia/src/quality_checks.py:36,53,73`)
  - Conector de clima e fetch Open‑Meteo sem API key
- Modelos preditivos:
  - Validação cruzada temporal (expanding/rolling)
  - Comparação de modelos e diagnóstico de resíduos por hora
- Dashboards:
  - Visualização das figuras EDA/MVP/H₂ e métricas
  - Rota dedicada a H₂ e opcional “toggle” para separar eixos
- Documentação:
  - Metodologias, premissas e referências — `docs/apresentacao_projeto_pjm.md`, `docs/estado_codigo_atual.md`

## Plano de Implementação
- Fase 1:
  - Integrar clima no pipeline de energia (join por `Datetime`)
  - Treinar modelos com clima (v2+) e avaliar ganhos nos horários críticos
  - Atualizar relatório com sumário executivo e CV
- Fase 2:
  - Ingerir irradiância e dataset H₂
  - Estimar produção de H₂ e integrar com sinais de carga
  - Construir análise econômica básica e otimização de alocação

## Execução
- Energia (MVP): `python Consumo Horário de Energia/mvp_energy.py`
- Clima:
  - Baixar: `python src/meteo_fetch_openmeteo.py LAT LON START END`
  - Integrar: `from src.meteo_ingest import load_meteo_dir, join_meteo`
- H₂: `python Consumo Horário de Energia/src/cli.py`
- Dashboard: `python Consumo Horário de Energia/src/dashboard_server.py` → `http://localhost:8000/`
