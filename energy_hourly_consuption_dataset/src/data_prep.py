import os
import pandas as pd
try:
    from src import meteo_ingest
except ImportError:
    import meteo_ingest

def load_raw(root):
    raw = os.path.join(root, 'data', 'raw')
    series = {}
    for name in os.listdir(raw):
        if not name.lower().endswith('.csv'):
            continue
        if name.endswith('_hourly.csv') or name == 'PJM_Load_hourly.csv':
            path = os.path.join(raw, name)
            df = pd.read_csv(path, low_memory=False)
            df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
            df = df.dropna(subset=['Datetime']).sort_values('Datetime')
            val_col = [c for c in df.columns if c != 'Datetime'][0]
            zone = val_col.replace('_MW', '')
            series[zone] = df[['Datetime', val_col]].rename(columns={val_col: zone})
    return series

def integrate(series):
    base = None
    for zone, df in series.items():
        if base is None:
            base = df.copy()
        else:
            base = pd.merge(base, df, on='Datetime', how='outer')
    return base

def write_csv(root, df, name):
    out_dir = os.path.join(root, 'data', 'processed')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    df.to_csv(path, index=False)
    return path

def main():
    root = os.getcwd()
    series = load_raw(root)
    integrated = integrate(series)
    
    # Weather integration
    meteo_df = meteo_ingest.load_meteo_dir(root)
    if meteo_df is not None:
        integrated = meteo_ingest.join_meteo(integrated, meteo_df)
        print("Weather data integrated.")
    else:
        print("No weather data found.")

    path_csv = write_csv(root, integrated, 'pjm_integrated.csv')
    print(f"CSV saved: {path_csv}")
    
    # Parquet support (optional)
    try:
        out_dir = os.path.join(root, 'data', 'processed')
        path_parquet = os.path.join(out_dir, 'pjm_dataset.parquet')
        integrated.to_parquet(path_parquet, index=False)
        print(f"Parquet saved: {path_parquet}")
    except ImportError:
        print("Parquet export skipped: pyarrow or fastparquet not found.")
    except Exception as e:
        print(f"Parquet export failed: {e}")

if __name__ == '__main__':
    main()
