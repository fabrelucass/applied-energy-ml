import os
import io
import re
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

ROOT = os.getcwd()

def read_operational_params():
    path = os.path.join(ROOT, 'configs', 'h2_params.yaml')
    params = {'capacity_mw': 10, 'kwh_per_kg': 52, 'offpeak_percentile': 25, 'emission_factor_kg_per_kwh': 0.0004}
    if not os.path.exists(path):
        return params
    text = open(path, 'r', encoding='utf-8').read()
    def find(key, cast=float):
        m = re.search(rf"{key}:\s*([0-9\.]+)", text)
        return cast(m.group(1)) if m else params[key]
    params['capacity_mw'] = find('capacity_mw')
    params['kwh_per_kg'] = find('kwh_per_kg')
    params['offpeak_percentile'] = find('offpeak_percentile', int)
    params['emission_factor_kg_per_kwh'] = find('emission_factor_kg_per_kwh')
    return params

def load_integrated():
    p1 = os.path.join(ROOT, 'data', 'processed', 'pjm_integrated.csv')
    p2 = os.path.join(ROOT, 'data', 'processed', 'pjm_dataset.csv')
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
    cols = [c for c in df.columns if c != 'Datetime']
    if 'PJM_Load' in cols:
        s = pd.to_numeric(df['PJM_Load'], errors='coerce')
    else:
        s = df[cols].apply(pd.to_numeric, errors='coerce').sum(axis=1)
    out = pd.DataFrame({'Datetime': df['Datetime'], 'load_total': s})
    return out

def add_calendar(df):
    d = df.copy()
    d['hora'] = d['Datetime'].dt.hour
    d['dia_semana'] = d['Datetime'].dt.dayofweek
    d['mes'] = d['Datetime'].dt.month
    return d

def compute_offpeak(df, percentile):
    s = pd.to_numeric(df['load_total'], errors='coerce')
    thr = float(np.nanpercentile(s.values, percentile))
    df['offpeak'] = s <= thr
    df['thr_load'] = thr
    return df

def estimate_h2(df, capacity_mw, kwh_per_kg, emission_factor_kg_per_kwh):
    d = df.copy()
    kw = float(capacity_mw) * 1000.0
    kg_per_h = kw / float(kwh_per_kg)
    d['h2_kg'] = np.where(d['offpeak'], kg_per_h, 0.0)
    d['co2e_kg_per_kg'] = float(emission_factor_kg_per_kwh) * float(kwh_per_kg)
    d['h2_co2e_kg'] = d['h2_kg'] * d['co2e_kg_per_kg']
    return d

def render_home(params, summary, images):
    html = []
    html.append('<html><head><title>Dashboard H2</title><meta http-equiv="refresh" content="30"></head><body>')
    html.append('<h1>Dashboard H2 – Dados PJM</h1>')
    html.append('<h2>Parâmetros</h2>')
    html.append(f"<p>Capacidade: {params['capacity_mw']} MW | Eficiência: {params['kwh_per_kg']} kWh/kg | Off-peak: {params['offpeak_percentile']}% | Fator emissões: {params['emission_factor_kg_per_kwh']} kg/kWh</p>")
    html.append('<h2>Sumário</h2>')
    html.append(f"<p>Horas off-peak: {summary['hours_offpeak']} | H2 total (kg): {summary['h2_total_kg']:.0f} | CO2e/kg: {summary['co2e_kg_per_kg']:.3f}</p>")
    ts = int(time.time())
    html.append(f"<h2>Potencial horário</h2><img src='/figure/h2_potential.png?ts={ts}' style='max-width:100%'>")
    html.append('<h2>Figuras EDA/MVP</h2>')
    html.append('<ul>')
    for name in images:
        html.append(f"<li><a href='/static/{name}' target='_blank'>{name}</a></li>")
    html.append('</ul>')
    html.append('</body></html>')
    return '\n'.join(html)

def list_images():
    d = os.path.join(ROOT, 'reports', 'figures')
    if not os.path.isdir(d):
        return []
    names = [n for n in os.listdir(d) if n.lower().endswith('.png')]
    return sorted(names)

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.startswith('/figure/h2_potential.png'):
                params = read_operational_params()
                df = load_integrated()
                load = select_load(df)
                load = add_calendar(load)
                load = compute_offpeak(load, params['offpeak_percentile'])
                res = estimate_h2(load, params['capacity_mw'], params['kwh_per_kg'], params['emission_factor_kg_per_kwh'])
                plt.figure(figsize=(12,5))
                sns.lineplot(x=res['Datetime'], y=res['load_total'], label='Load')
                sns.lineplot(x=res['Datetime'], y=res['h2_kg'], label='H2 kg/h')
                plt.legend()
                plt.tight_layout()
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                plt.close()
                data = buf.getvalue()
                self.send_response(200)
                self.send_header('Content-Type', 'image/png')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            if self.path.startswith('/static/'):
                name = self.path.split('/static/', 1)[1]
                full = os.path.join(ROOT, 'reports', 'figures', name)
                if os.path.isfile(full):
                    data = open(full, 'rb').read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'image/png')
                    self.send_header('Content-Length', str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                self.send_error(404)
                return
            params = read_operational_params()
            df = load_integrated()
            load = select_load(df)
            load = add_calendar(load)
            load = compute_offpeak(load, params['offpeak_percentile'])
            res = estimate_h2(load, params['capacity_mw'], params['kwh_per_kg'], params['emission_factor_kg_per_kwh'])
            hours_offpeak = int(res['offpeak'].sum())
            h2_total_kg = float(res['h2_kg'].sum())
            co2e_kg_per_kg = float(res['co2e_kg_per_kg'].iloc[0])
            images = list_images()
            html = render_home(params, {'hours_offpeak': hours_offpeak, 'h2_total_kg': h2_total_kg, 'co2e_kg_per_kg': co2e_kg_per_kg}, images)
            data = html.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            msg = f'Erro: {str(e)}'.encode('utf-8')
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Content-Length', str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)

def run_server(port=8000):
    httpd = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f'http://localhost:{port}/')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
