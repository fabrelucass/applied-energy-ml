import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)

def load_data(root):
    p = os.path.join(root, 'hybrid_energy_storage_dataset', 'hybrid_energy_storage.csv')
    df = pd.read_csv(p, low_memory=False)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df = df.dropna(subset=['Timestamp']).sort_values('Timestamp')
    for c in ['Solar_Power_kW','Wind_Power_kW','Grid_Power_kW','Battery_SoC_%','SC_Charge_kW','Hydrogen_Production_kg/h','Load_Demand_kW','Power_Supplied_kW','Power_Loss_kW']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return df

def compute_metrics(df):
    d = df.copy()
    d['balance_resid'] = d['Power_Supplied_kW'] - (d['Load_Demand_kW'] + d['Power_Loss_kW'])
    d['coverage'] = d['Power_Supplied_kW'] / d['Load_Demand_kW']
    denom_supply = d['Power_Supplied_kW'].replace(0, np.nan)
    d['loss_rate'] = d['Power_Loss_kW'] / denom_supply
    d['grid_share'] = d['Grid_Power_kW'] / denom_supply
    surplus_kw = np.maximum(d['Power_Supplied_kW'] - d['Load_Demand_kW'], 0.0)
    denom_surplus = surplus_kw.replace(0, np.nan)
    d['h2_kg_per_kwh_surplus'] = d['Hydrogen_Production_kg/h'] / denom_surplus
    grp = d.groupby('Optimization_Level')
    t = grp.agg({
        'coverage':'mean',
        'loss_rate':'mean',
        'grid_share':'mean',
        'Battery_SoC_%':'mean',
        'SC_Charge_kW':'std',
        'Hydrogen_Production_kg/h':'mean',
        'h2_kg_per_kwh_surplus':'mean',
        'balance_resid':'mean'
    }).reset_index()
    return d, t

def plot_bars(table, out_dir):
    ensure_dir(out_dir)
    levels = table['Optimization_Level'].tolist()
    plt.figure(figsize=(8,5))
    plt.bar(levels, table['coverage'])
    plt.ylabel('Coverage (Supplied/Demand)')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'coverage_by_level.png'))
    plt.close()
    plt.figure(figsize=(8,5))
    plt.bar(levels, table['loss_rate'])
    plt.ylabel('Loss Rate (Loss/Supplied)')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'loss_rate_by_level.png'))
    plt.close()
    plt.figure(figsize=(8,5))
    plt.bar(levels, table['grid_share'])
    plt.ylabel('Grid Share (Grid/Supplied)')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'grid_share_by_level.png'))
    plt.close()

def plot_timeseries(df, out_dir, n=96):
    ensure_dir(out_dir)
    s = df.sort_values('Timestamp').iloc[:n]
    plt.figure(figsize=(12,5))
    plt.plot(s['Timestamp'], s['Load_Demand_kW'], label='Demand')
    plt.plot(s['Timestamp'], s['Power_Supplied_kW'], label='Supplied')
    plt.plot(s['Timestamp'], s['Hydrogen_Production_kg/h']*10.0, label='H2 kg/h x10')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'sample_timeseries.png'))
    plt.close()

def write_report(root, df, table):
    out_dir = os.path.join(root, 'hybrid_energy_storage_dataset', 'figures')
    ensure_dir(out_dir)
    plot_bars(table, out_dir)
    plot_timeseries(df, out_dir)
    path = os.path.join(root, 'hybrid_energy_storage_dataset', 'HESS_benchmark.md')
    lines = []
    lines.append('# Benchmark de Operação — Hybrid Energy Storage')
    lines.append('')
    lines.append(f'Linhas: {len(df)}')
    lines.append(f'Período: {df["Timestamp"].min()} a {df["Timestamp"].max()}')
    lines.append('')
    lines.append('## Métricas por Optimization_Level')
    lines.append('| Level | Coverage | Loss Rate | Grid Share | SoC Médio | SC Volatilidade | H2 kg/h | H2 kg/kWh surplus | Balance Residual |')
    lines.append('|---|---:|---:|---:|---:|---:|---:|---:|---:|')
    for _, r in table.iterrows():
        lines.append(f'| {r["Optimization_Level"]} | {r["coverage"]:.3f} | {r["loss_rate"]:.3f} | {r["grid_share"]:.3f} | {r["Battery_SoC_%"]:.2f} | {r["SC_Charge_kW"]:.3f} | {r["Hydrogen_Production_kg/h"]:.3f} | {r["h2_kg_per_kwh_surplus"]:.5f} | {r["balance_resid"]:.3f} |')
    lines.append('')
    lines.append('## Figuras')
    lines.append('- `figures/coverage_by_level.png`')
    lines.append('- `figures/loss_rate_by_level.png`')
    lines.append('- `figures/grid_share_by_level.png`')
    lines.append('- `figures/sample_timeseries.png`')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(path)

def main():
    root = os.getcwd()
    df = load_data(root)
    df, table = compute_metrics(df)
    write_report(root, df, table)

if __name__ == '__main__':
    main()

