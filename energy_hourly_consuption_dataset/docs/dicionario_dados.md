# Dicionário de Dados

## Colunas por arquivo (raw)
- `Datetime`: data e hora no fuso do dataset (formato `YYYY-MM-DD HH:MM:SS`)
- `*_MW`: carga em megawatts (MW) para a zona indicada

## Colunas no dataset integrado
- `Datetime`: chave temporal
- `AEP`, `COMED`, `DAYTON`, `DEOK`, `DOM`, `DUQ`, `EKPC`, `FE`, `NI`, `PJME`, `PJMW`, `PJM_Load`: cargas MW por zona

## Tipos e unidades
- `Datetime`: datetime
- cargas: float (MW)

## Regras de qualidade
- `Datetime` não nulo e ordenado
- Sem duplicatas por `Datetime` em cada série
- Faixas plausíveis de MW por zona
