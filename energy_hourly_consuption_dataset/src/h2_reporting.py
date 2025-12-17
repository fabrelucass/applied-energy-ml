import os
import seaborn as sns
import matplotlib.pyplot as plt

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)

def plot_potential(df, out_path):
    plt.figure(figsize=(12,5))
    sns.lineplot(x=df['Datetime'], y=df['load_total'], label='Load')
    sns.lineplot(x=df['Datetime'], y=df['h2_kg'], label='H2 kg/h')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def write_report(path, params, summary):
    lines = []
    lines.append('# Relatório H2: Potencial Operacional com Dados PJM')
    lines.append('')
    lines.append(f"Capacidade do eletrolisador: {params['capacity_mw']} MW")
    lines.append(f"Eficiência: {params['kwh_per_kg']} kWh/kg")
    lines.append(f"Percentil off-peak: {params['offpeak_percentile']}%")
    lines.append('')
    lines.append('## Sumário')
    lines.append(f"Horas off-peak: {summary['hours_offpeak']}")
    lines.append(f"H2 total estimado (kg): {summary['h2_total_kg']:.2f}")
    lines.append(f"CO2e por kg estimado (kg/kg): {summary['co2e_kg_per_kg']:.3f}")
    lines.append('')
    lines.append('## Observações')
    lines.append('Resultados dependem de parâmetros; preços e emissões reais devem ser integrados para LCOH e intensidade de carbono certificável.')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

