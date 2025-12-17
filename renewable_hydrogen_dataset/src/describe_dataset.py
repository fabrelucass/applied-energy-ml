import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)

def load_dataset(root):
    path = os.path.join(root, 'renewable_hydrogen_dataset', 'renewable_hydrogen_dataset.csv')
    df = pd.read_csv(path, low_memory=False)
    return df

def summarize_schema(df):
    rows = []
    for c in df.columns:
        dtype = str(df[c].dtype)
        missing = int(df[c].isna().sum())
        nonnull = int(df[c].notna().sum())
        rows.append({'column': c, 'dtype': dtype, 'missing': missing, 'non_null': nonnull})
    schema = pd.DataFrame(rows)
    return schema

def numeric_stats(df):
    num = df.select_dtypes(include=[np.number])
    if num.empty:
        return pd.DataFrame()
    stats = num.describe().T.reset_index().rename(columns={'index': 'column'})
    return stats[['column','mean','std','min','25%','50%','75%','max']]

def categorical_top_values(df, topn=10):
    cat = df.select_dtypes(exclude=[np.number])
    rows = []
    for c in cat.columns:
        vc = df[c].value_counts(dropna=True).head(topn)
        rows.append({'column': c, 'top_values': '; '.join([f'{k}:{int(v)}' for k, v in vc.items()])})
    return pd.DataFrame(rows)

def plot_numeric_histograms(df, out_dir, max_plots=12):
    num = df.select_dtypes(include=[np.number])
    cols = list(num.columns)[:max_plots]
    figs = []
    for c in cols:
        plt.figure(figsize=(8,5))
        sns.histplot(num[c].dropna(), bins=40, kde=True)
        plt.title(f"Histograma {c}")
        plt.xlabel(c)
        plt.tight_layout()
        p = os.path.join(out_dir, f"rh_hist_{c}.png")
        plt.savefig(p)
        plt.close()
        figs.append(p)
    return figs

def plot_corr_heatmap(df, out_dir):
    num = df.select_dtypes(include=[np.number]).copy()
    if num.empty:
        return None
    corr = num.corr(numeric_only=True)
    plt.figure(figsize=(10,8))
    sns.heatmap(corr, cmap='viridis')
    plt.title("Correlação (numérica)")
    plt.tight_layout()
    p = os.path.join(out_dir, "rh_corr_heatmap.png")
    plt.savefig(p)
    plt.close()
    return p

def write_markdown(root, schema, num_stats, cat_top, figs, corr_fig):
    docs = os.path.join(root, 'renewable_hydrogen_dataset', 'docs')
    ensure_dir(docs)
    path = os.path.join(docs, 'dataset_overview.md')
    lines = []
    lines.append("# Overview — renewable_hydrogen_dataset.csv")
    lines.append("")
    lines.append("## Schema")
    lines.append("| Column | Dtype | Missing | Non-null |")
    lines.append("|---|---|---:|---:|")
    for _, r in schema.iterrows():
        lines.append(f"| {r['column']} | {r['dtype']} | {int(r['missing'])} | {int(r['non_null'])} |")
    lines.append("")
    if not num_stats.empty:
        lines.append("## Numeric Stats")
        lines.append("| Column | Mean | Std | Min | P25 | P50 | P75 | Max |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        for _, r in num_stats.iterrows():
            lines.append(f"| {r['column']} | {float(r['mean']):.3f} | {float(r['std']):.3f} | {float(r['min']):.3f} | {float(r['25%']):.3f} | {float(r['50%']):.3f} | {float(r['75%']):.3f} | {float(r['max']):.3f} |")
        lines.append("")
    if not cat_top.empty:
        lines.append("## Categorical Top Values")
        lines.append("| Column | Top values (count) |")
        lines.append("|---|---|")
        for _, r in cat_top.iterrows():
            lines.append(f"| {r['column']} | {r['top_values']} |")
        lines.append("")
    if figs:
        lines.append("## Histograms")
        for p in figs:
            lines.append(f"- {os.path.basename(p)}")
        lines.append("")
    if corr_fig:
        lines.append("## Correlation")
        lines.append(f"- {os.path.basename(corr_fig)}")
        lines.append("")
    with open(path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    return path

def main():
    root = os.getcwd()
    df = load_dataset(root)
    schema = summarize_schema(df)
    num_stats = numeric_stats(df)
    cat_top = categorical_top_values(df)
    figs_dir = os.path.join(root, 'renewable_hydrogen_dataset', 'reports', 'figures')
    ensure_dir(figs_dir)
    figs = plot_numeric_histograms(df, figs_dir)
    corr = plot_corr_heatmap(df, figs_dir)
    md = write_markdown(root, schema, num_stats, cat_top, figs, corr)
    print(md)

if __name__ == '__main__':
    main()
