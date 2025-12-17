import os
import pandas as pd

def load_meteo_csv(path):
    df = pd.read_csv(path, low_memory=False)
    df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
    df = df.dropna(subset=['Datetime']).sort_values('Datetime')
    for c in ['temp_c', 'wind_ms', 'irradiance_wm2']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    return df

def load_meteo_dir(root):
    d = os.path.join(root, 'data', 'external', 'meteo')
    if not os.path.isdir(d):
        return None
    frames = []
    for name in os.listdir(d):
        if name.lower().endswith('.csv'):
            p = os.path.join(d, name)
            frames.append(load_meteo_csv(p))
    if not frames:
        return None
    df = pd.concat(frames, axis=0, ignore_index=True)
    df = df.drop_duplicates(subset=['Datetime']).sort_values('Datetime')
    return df

def join_meteo(load_df, meteo_df):
    if meteo_df is None:
        return load_df
    out = pd.merge(load_df, meteo_df, on='Datetime', how='left')
    return out
