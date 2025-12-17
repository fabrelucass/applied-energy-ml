# Google Colab — Projeto H₂

## Estrutura de Pastas no Drive
- Crie `MyDrive/h2_project/`
- Subpastas obrigatórias:
  - `hybrid_energy_storage_dataset/` → coloque `hybrid_energy_storage.csv`
  - `renewable_hydrogen_dataset/` → coloque `renewable_hydrogen_dataset_2535.csv`
  - `external/` → indicadores auxiliares:
    - `emissions_per_capita.csv` (Country, Emissions_per_capita)
    - `renewables_share.csv` (Country, Renewables_share)
    - `gdp_per_capita.csv` (Country, GDP_per_capita)
    - `electricity_access.csv` (Country, Electricity_access)
    - `city_to_country.csv` (City, Country)
    - `h2_consumption.csv` (Country, H2_grey_kg_per_year)
  - `outputs/` → arquivos de saída (gerados pelo notebook)

## Fluxo no Notebook
- Setup de dependências
- Montagem do Drive
- Carregamento dos datasets (HESS e H₂ por cidade)
- EDA e KPIs (balanço energético e estatísticas)
- Cálculo do índice de atratividade de hubs de H₂
- Simulação de substituição H₂ cinza→verde e redução de CO₂
- Exportação de rankings e resultados em `outputs/`

## Observações
- Normalize unidades e nomes de colunas conforme os arquivos indicados.
- Ajuste os pesos do índice conforme sua estratégia de priorização.

