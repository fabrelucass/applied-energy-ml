import os
import json
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import yaml

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_dirs(cfg):
    os.makedirs(cfg["reports_dir"], exist_ok=True)
    os.makedirs(cfg["figures_dir"], exist_ok=True)

def read_data(cfg):
    return pd.read_csv(cfg["data_path"])

def describe(df, numeric_columns):
    desc = df[numeric_columns].describe(percentiles=[0.25,0.5,0.75]).T
    return desc

def missing(df):
    return df.isna().sum()

def plot_histograms(df, numeric_columns, out_dir):
    for c in numeric_columns:
        plt.figure()
        sns.histplot(df[c].dropna(), kde=True)
        plt.title(f"Histogram {c}")
        p = os.path.join(out_dir, f"hist_{c}.png")
        plt.savefig(p, bbox_inches="tight")
        plt.close()

def plot_boxplots(df, numeric_columns, out_dir):
    for c in numeric_columns:
        plt.figure()
        sns.boxplot(x=df[c].dropna())
        plt.title(f"Boxplot {c}")
        p = os.path.join(out_dir, f"box_{c}.png")
        plt.savefig(p, bbox_inches="tight")
        plt.close()

def plot_correlation(df, numeric_columns, out_dir):
    corr = df[numeric_columns].corr()
    plt.figure(figsize=(10,8))
    sns.heatmap(corr, cmap="viridis")
    p = os.path.join(out_dir, "corr_heatmap.png")
    plt.savefig(p, bbox_inches="tight")
    plt.close()
    return corr

def write_report(cfg, desc, miss, corr):
    report_path = os.path.join(cfg["reports_dir"], "eda_report.json")
    obj = {"descriptive": desc.to_dict(), "missing": miss.to_dict(), "correlation": {} if corr is None else corr.to_dict()}
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def run(config_path):
    cfg = load_config(config_path)
    ensure_dirs(cfg)
    df = read_data(cfg)
    desc = describe(df, cfg["numeric_columns"])
    miss = missing(df)
    if cfg["eda"]["histograms"]:
        plot_histograms(df, cfg["numeric_columns"], cfg["figures_dir"])
    if cfg["eda"]["boxplots"]:
        plot_boxplots(df, cfg["numeric_columns"], cfg["figures_dir"])
    corr = None
    if cfg["eda"]["correlation"]:
        corr = plot_correlation(df, cfg["numeric_columns"], cfg["figures_dir"])
    write_report(cfg, desc, miss, corr)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    run(args.config)
