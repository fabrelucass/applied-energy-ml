import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "Load profile data of 50 industrial plants")

def load_data():
    df_2016 = pd.read_csv(
        os.path.join(DATA_DIR, "LoadProfile_20IPs_2016.csv"),
        sep=";", header=1, low_memory=False
    ).rename(columns={"Time stamp": "timestamp"})
    df_2017 = pd.read_csv(
        os.path.join(DATA_DIR, "LoadProfile_30IPs_2017.csv"),
        sep=";", header=1, low_memory=False
    ).rename(columns={"Time stamp": "timestamp"})
    df_long_16 = df_2016.melt(id_vars="timestamp", var_name="plant_id", value_name="load_kW")
    df_long_16["plant_id"] = "2016_" + df_long_16["plant_id"].str.replace("LG ", "")
    df_long_17 = df_2017.melt(id_vars="timestamp", var_name="plant_id", value_name="load_kW")
    df_long_17["plant_id"] = "2017_" + df_long_17["plant_id"].str.replace("LG ", "")
    df = pd.concat([df_long_16, df_long_17], ignore_index=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["load_kW"] = df["load_kW"].astype(str).str.replace(",", ".").replace("", "0").astype(float)
    return df

def summarize(df):
    df["hour"] = df["timestamp"].dt.hour
    df["dayofweek"] = df["timestamp"].dt.dayofweek
    g = df.groupby("plant_id")["load_kW"]
    stats = pd.DataFrame({
        "count": g.size(),
        "mean": g.mean(),
        "std": g.std(),
        "min": g.min(),
        "p25": g.quantile(0.25),
        "median": g.quantile(0.5),
        "p75": g.quantile(0.75),
        "max": g.max()
    }).reset_index()
    # Hourly profile stability: std of hourly means
    hourly = df.groupby(["plant_id", "hour"])["load_kW"].mean().reset_index()
    stab = hourly.groupby("plant_id")["load_kW"].std().rename("hourly_profile_std").reset_index()
    out = stats.merge(stab, on="plant_id", how="left")
    return out

def main():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    df = load_data()
    summary = summarize(df)
    path = os.path.join(REPORTS_DIR, "eda_summary.csv")
    summary.to_csv(path, index=False)
    print(path)

if __name__ == "__main__":
    main()
