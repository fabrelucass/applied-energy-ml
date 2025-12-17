# MVP Analítico: Consumo Horário de Energia (PJM)

Contexto: Suavização de curva de carga e identificação de picos/vales

## Sumário Executivo

| Modelo | MAE (teste) | RMSE (teste) |
|---|---:|---:|
| Baseline lag‑1 | 415.14 | 525.10 |
| Linear v1 | 392.01 | 491.75 |
| Linear v2 | 392.08 | 491.82 |

## Introdução
Entender padrões básicos (hora, dia, estação) e identificar picos/vales para flexibilidade.

## Carregamento e preparação
Arquivos: AEP_hourly.csv e PJM_Load_hourly.csv. Conversão de `Datetime` e criação de hora, dia da semana, mês, ano, estação.

## EDA básica
Histogramas:
- `mvp_hist_AEP.png`
- `mvp_hist_PJM_Load.png`
Curvas médias por hora (ano de teste):
- AEP: `mvp_hourcurve_AEP_2018.png`
- PJM_Load: `mvp_hourcurve_PJM_Load_2018.png`
Curva média por dia da semana:
- AEP: `mvp_dowcurve_AEP.png`
- PJM_Load: `mvp_dowcurve_PJM_Load.png`
Top horas de verão (AEP):
- hora 17: 19031.2 MW
- hora 18: 18956.4 MW
- hora 16: 18924.9 MW
Top horas de inverno (AEP):
- hora 20: 18172.7 MW
- hora 19: 18129.4 MW
- hora 9: 18109.9 MW

## Métricas simples de fator de carga
Tabela salva: `mvp_daily_load_factor_AEP.csv`
Dias com menor fator de carga:
- 2008-10-20 fator 0.626 média 16079.9 pico 25695.0
- 2016-09-05 fator 0.758 média 13826.3 pico 18234.0
- 2017-09-24 fator 0.773 média 14332.2 pico 18548.0
- 2010-08-29 fator 0.775 média 15681.7 pico 20245.0
- 2015-12-27 fator 0.775 média 11998.9 pico 15488.0
- 2012-06-29 fator 0.777 média 18119.7 pico 23320.0
- 2015-09-07 fator 0.777 média 15242.5 pico 19614.0
- 2018-07-08 fator 0.777 média 13768.7 pico 17710.0
- 2017-08-20 fator 0.778 média 14981.8 pico 19249.0
- 2016-09-06 fator 0.781 média 16849.3 pico 21580.0
Relação pico vs média: `mvp_peak_vs_mean_AEP.png`

## Modelo de previsão básico (AEP)
Período de teste: 2018
Baseline (lag 1h): MAE=415.14 RMSE=525.10
Regressão Linear (hora, dia_semana, mês, lag1, lag24): MAE=392.01 RMSE=491.75

## Comparação de modelos
- Linear v1 (lags+calendário): MAE=392.01 RMSE=491.75
- Linear v2 (lags+calendário+fim_semana): MAE=392.08 RMSE=491.82

- Erro por hora (v1 vs v2): `mvp_resid_hour_model_compare_AEP.png`

Top horários por ganho (MAE_v1 − MAE_v2):
| Hora | MAE v1 | MAE v2 | Ganho |
|---:|---:|---:|---:|
| 6 | 431.84 | 430.54 | 1.29 |
| 7 | 668.71 | 667.72 | 0.98 |
| 18 | 286.13 | 285.47 | 0.66 |
| 12 | 398.38 | 397.72 | 0.66 |
| 14 | 340.48 | 340.04 | 0.44 |
Arquivo completo: `mvp_hourly_error_compare_AEP.csv`

Piores horários (ganho negativo ou menor):
| Hora | MAE v1 | MAE v2 | Ganho |
|---:|---:|---:|---:|
| 2 | 383.12 | 384.45 | -1.33 |
| 3 | 291.10 | 292.41 | -1.31 |
| 15 | 299.48 | 300.37 | -0.89 |
| 5 | 202.73 | 203.42 | -0.69 |
| 4 | 223.09 | 223.71 | -0.62 |

Ganho por hora (figura): `mvp_hourly_improvement_AEP.png`

## Validação temporal
Expanding window (MAE/RMSE por ano de teste):
- 2016: MAE=394.37 RMSE=501.61
- 2017: MAE=371.55 RMSE=473.08
- 2018: MAE=392.01 RMSE=491.75
Rolling window (MAE/RMSE por ano de teste):
- 2016: MAE=392.10 RMSE=501.56
- 2017: MAE=369.32 RMSE=471.62
- 2018: MAE=389.14 RMSE=489.67

Validação temporal (modelo v2)
Expanding window (MAE/RMSE por ano de teste):
- 2016: MAE=394.45 RMSE=501.61
- 2017: MAE=371.96 RMSE=473.45
- 2018: MAE=392.08 RMSE=491.82
Rolling window (MAE/RMSE por ano de teste):
- 2016: MAE=392.13 RMSE=501.50
- 2017: MAE=369.56 RMSE=471.73
- 2018: MAE=389.32 RMSE=489.94

## Diagnóstico de resíduos
- Histograma de resíduos: `mvp_resid_hist_AEP.png`
- Erro por hora do dia: `mvp_resid_hour_AEP.png`

Diagnóstico de resíduos (modelo v2)
- Histograma de resíduos: `mvp_resid_hist_AEP_v2.png`
- Erro por hora do dia: `mvp_resid_hour_AEP_v2.png`
- Erro por hora (feriado vs não feriado): `mvp_resid_hour_holiday_AEP_v2.png`

## Conexão com elasticidade e smart energy
Identificar janelas de pico e vale próximas como candidatos a deslocamento. Próximo passo: conectar variação de carga à elasticidade do processo para simular suavização.