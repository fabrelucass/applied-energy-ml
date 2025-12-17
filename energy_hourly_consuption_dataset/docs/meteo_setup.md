# Integração de Clima (MVP)

## Fontes recomendadas
- Open‑Meteo (grátis, sem API key): histórico horário de temperatura, vento e radiação.
- Weatherbit/OpenWeather/NASA POWER/ERA5: opções mais completas para energia/solar.

## Passos rápidos com Open‑Meteo
1) Baixar clima horário:
   - `python src/meteo_fetch_openmeteo.py 39.9612 -82.9988 2018-01-01 2018-12-31`
   - Ou defina env: `OM_LAT`, `OM_LON`, `OM_START`, `OM_END`, `OM_TZ` e rode sem argumentos.
2) O CSV será salvo em `data/external/meteo/openmeteo_<lat>_<lon>_<start>_<end>.csv`.
3) Ingestão e join:
   - `from src.meteo_ingest import load_meteo_dir, join_meteo`
   - `meteo = load_meteo_dir(<root>)`
   - `load = join_meteo(load, meteo)` com colunas `Datetime`, `temp_c`, `wind_ms`, `irradiance_wm2`.

## Observações
- Sem dependências extras: usa `urllib` e `json` da biblioteca padrão e `pandas`.
- Para múltiplas localidades, salve vários CSVs na pasta `data/external/meteo` e o conector agregará por `Datetime`.
