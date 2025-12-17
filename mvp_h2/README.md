# MVP H₂ – EDA, Limpeza, Features, Modelo e Deploy

## Objetivo
- Executar uma análise exploratória, limpeza, engenharia de features e treinar um modelo para prever `Optimization_Level` usando `hybrid_energy_storage_dataset/hybrid_energy_storage.csv`.
- Disponibilizar uma API para predição e um fluxo reprodutível com configuração.

## Estrutura
- `configs/config.yaml`: caminhos e parâmetros
- `src/eda.py`: relatórios e figuras
- `src/clean.py`: processamento e limpeza
- `src/features.py`: seleção e criação de features
- `src/model.py`: treino e avaliação
- `src/pipeline.py`: CLI orquestradora
- `src/api.py`: serviço FastAPI
- `reports/figures/`: visualizações
- `artifacts/`: modelos e pré-processadores salvos
- `requirements.txt`: dependências
- `Dockerfile`: container para API

## Uso Rápido
```
python -m mvp_h2.src.pipeline --config mvp_h2/configs/config.yaml --task eda
python -m mvp_h2.src.pipeline --config mvp_h2/configs/config.yaml --task train
python -m mvp_h2.src.pipeline --config mvp_h2/configs/config.yaml --task predict --input mvp_h2/sample_input.json
```

## API
```
uvicorn mvp_h2.src.api:app --host 0.0.0.0 --port 8000
```

## Docker
```
docker build -t h2-mvp -f mvp_h2/Dockerfile .
docker run -p 8000:8000 h2-mvp
```

