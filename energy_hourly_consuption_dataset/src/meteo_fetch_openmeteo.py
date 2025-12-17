import os
import sys
import json
import urllib.request
import urllib.parse
import pandas as pd

def fetch_open_meteo(lat, lon, start_date, end_date, timezone='auto'):
    base = 'https://archive-api.open-meteo.com/v1/archive'
    params = {
        'latitude': float(lat),
        'longitude': float(lon),
        'start_date': start_date,
        'end_date': end_date,
        'hourly': 'temperature_2m,wind_speed_10m,shortwave_radiation',
        'timezone': timezone
    }
    url = base + '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    h = data.get('hourly', {})
    times = h.get('time', [])
    t2m = h.get('temperature_2m', [])
    w10 = h.get('wind_speed_10m', [])
    sw = h.get('shortwave_radiation', [])
    df = pd.DataFrame({
        'Datetime': pd.to_datetime(times, errors='coerce'),
        'temp_c': pd.to_numeric(pd.Series(t2m), errors='coerce'),
        'wind_ms': pd.to_numeric(pd.Series(w10), errors='coerce'),
        'irradiance_wm2': pd.to_numeric(pd.Series(sw), errors='coerce')
    })
    df = df.dropna(subset=['Datetime']).sort_values('Datetime')
    return df

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)

def save_csv(root, df, name):
    d = os.path.join(root, 'data', 'external', 'meteo')
    ensure_dir(d)
    path = os.path.join(d, name)
    df.to_csv(path, index=False)
    return path

def main():
    root = os.getcwd()
    if len(sys.argv) >= 5:
        lat = float(sys.argv[1])
        lon = float(sys.argv[2])
        start = sys.argv[3]
        end = sys.argv[4]
    else:
        lat = float(os.environ.get('OM_LAT', 39.9612))
        lon = float(os.environ.get('OM_LON', -82.9988))
        start = os.environ.get('OM_START', '2018-01-01')
        end = os.environ.get('OM_END', '2018-12-31')
    tz = os.environ.get('OM_TZ', 'auto')
    df = fetch_open_meteo(lat, lon, start, end, tz)
    name = f'openmeteo_{lat}_{lon}_{start}_{end}.csv'.replace(':', '-')
    p = save_csv(root, df, name)
    print(p)

if __name__ == '__main__':
    main()
