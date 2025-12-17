import os
import pandas as pd

def load_integrated(root):
    p1 = os.path.join(root, 'data', 'processed', 'pjm_integrated.csv')
    p2 = os.path.join(root, 'data', 'processed', 'pjm_dataset.csv')
    if os.path.exists(p1):
        df = pd.read_csv(p1, low_memory=False)
    elif os.path.exists(p2):
        df = pd.read_csv(p2, low_memory=False)
    else:
        raise FileNotFoundError('Integrated dataset not found')
    df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
    df = df.dropna(subset=['Datetime']).sort_values('Datetime')
    return df

def select_load(df):
    cols = [c for c in df.columns if c not in ['Datetime']]
    if 'PJM_Load' in cols:
        s = pd.to_numeric(df['PJM_Load'], errors='coerce')
    else:
        s = df[cols].apply(pd.to_numeric, errors='coerce').sum(axis=1)
    out = pd.DataFrame({'Datetime': df['Datetime'], 'load_total': s})
    return out

