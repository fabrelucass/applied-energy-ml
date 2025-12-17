import os
import yaml
import pandas as pd
from h2_ingest import load_integrated, select_load
from h2_features import add_calendar, compute_offpeak_flags, estimate_h2_potential
from h2_reporting import ensure_dir, plot_potential, write_report
from meteo_ingest import load_meteo_dir, join_meteo

def read_params(root):
    path = os.path.join(root, 'configs', 'h2_params.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    root = os.getcwd()
    params = read_params(root)
    df = load_integrated(root)
    load = select_load(df)
    meteo = load_meteo_dir(root)
    if meteo is not None:
        load = join_meteo(load, meteo)
    load = add_calendar(load)
    op = params['operational']
    load = compute_offpeak_flags(load, op['offpeak_percentile'])
    pv_coeff = op.get('pv_coeff_mw_per_wm2', None)
    res = estimate_h2_potential(load, op['capacity_mw'], op['kwh_per_kg'], op['emission_factor_kg_per_kwh'], pv_coeff_mw_per_wm2=pv_coeff)
    figs = os.path.join(root, params['pipeline']['outputs']['figures'])
    ensure_dir(figs)
    plot_path = os.path.join(figs, 'h2_potential.png')
    plot_potential(res, plot_path)
    hours_offpeak = int(res['offpeak'].sum())
    h2_total_kg = float(res['h2_kg'].sum())
    co2e_kg_per_kg = float(res['co2e_kg_per_kg'].iloc[0])
    reports = os.path.join(root, params['pipeline']['outputs']['reports'])
    ensure_dir(reports)
    rep_path = os.path.join(reports, 'h2_report.md')
    write_report(rep_path, op, {'hours_offpeak': hours_offpeak, 'h2_total_kg': h2_total_kg, 'co2e_kg_per_kg': co2e_kg_per_kg})
    print(rep_path)

if __name__ == '__main__':
    main()
