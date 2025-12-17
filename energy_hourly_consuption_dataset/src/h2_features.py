import numpy as np
import pandas as pd

def add_calendar(df):
    d = df.copy()
    d['hora'] = d['Datetime'].dt.hour
    d['dia_semana'] = d['Datetime'].dt.dayofweek
    d['mes'] = d['Datetime'].dt.month
    return d

def compute_offpeak_flags(df, percentile):
    s = pd.to_numeric(df['load_total'], errors='coerce')
    thr = float(np.nanpercentile(s.values, percentile))
    df['offpeak'] = s <= thr
    df['thr_load'] = thr
    return df

def estimate_h2_potential(df, capacity_mw, kwh_per_kg, emission_factor_kg_per_kwh, pv_coeff_mw_per_wm2=None):
    d = df.copy()
    kw = float(capacity_mw) * 1000.0
    kwh_per_kg = float(kwh_per_kg)
    if pv_coeff_mw_per_wm2 is not None and 'irradiance_wm2' in d.columns:
        coeff = float(pv_coeff_mw_per_wm2)
        d['pv_mw'] = d['irradiance_wm2'].astype(float) * coeff
        d['pv_kw'] = d['pv_mw'] * 1000.0
        d['kw_available'] = np.minimum(d['pv_kw'], kw)
    else:
        d['pv_mw'] = np.nan
        d['pv_kw'] = np.nan
        d['kw_available'] = kw
    d['h2_kw'] = np.where(d['offpeak'], d['kw_available'], 0.0)
    d['h2_kg'] = d['h2_kw'] / kwh_per_kg
    d['co2e_kg_per_kg'] = float(emission_factor_kg_per_kwh) * float(kwh_per_kg)
    d['h2_co2e_kg'] = d['h2_kg'] * d['co2e_kg_per_kg']
    return d
