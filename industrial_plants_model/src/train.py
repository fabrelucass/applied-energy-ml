
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import OrdinalEncoder
import joblib
import json
import warnings

warnings.filterwarnings('ignore')

# --- Config ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "Load profile data of 50 industrial plants")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

def load_data():
    print("Loading data...")
    # Load 2016
    df_2016 = pd.read_csv(
        os.path.join(DATA_DIR, "LoadProfile_20IPs_2016.csv"),
        sep=";", header=1, low_memory=False
    )
    df_2016 = df_2016.rename(columns={"Time stamp": "timestamp"})
    
    # Load 2017
    df_2017 = pd.read_csv(
        os.path.join(DATA_DIR, "LoadProfile_30IPs_2017.csv"),
        sep=";", header=1, low_memory=False
    )
    df_2017 = df_2017.rename(columns={"Time stamp": "timestamp"})

    # Melt and Unique IDs
    print("Melting 2016...")
    df_long_16 = df_2016.melt(id_vars="timestamp", var_name="plant_id", value_name="load_kW")
    df_long_16["plant_id"] = "2016_" + df_long_16["plant_id"].str.replace("LG ", "")
    
    print("Melting 2017...")
    df_long_17 = df_2017.melt(id_vars="timestamp", var_name="plant_id", value_name="load_kW")
    df_long_17["plant_id"] = "2017_" + df_long_17["plant_id"].str.replace("LG ", "")
    
    # Concat
    df = pd.concat([df_long_16, df_long_17], ignore_index=True)
    
    # Parse timestamps
    print("Parsing timestamps...")
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d.%m.%Y %H:%M:%S", errors='coerce')
    df = df.dropna(subset=["timestamp"])
    
    # Clean load_kW
    df["load_kW"] = df["load_kW"].astype(str).str.replace(",", ".").replace("", "0").astype(float)
    
    df = df.sort_values(["plant_id", "timestamp"]).reset_index(drop=True)
    
    # --- Load Weather Data (2018-2023) ---
    print("Loading Weather Data Proxy...")
    weather_df = pd.read_csv(
        os.path.join(os.path.dirname(DATA_DIR), "Hourly Power Load and Climate Data", "PowerLoad_Dataset.csv")
    )
    weather_df["Timestamp"] = pd.to_datetime(weather_df["Timestamp"])
    
    # Create a proxy by averaging weather by Month, Day, Hour
    weather_df["month"] = weather_df["Timestamp"].dt.month
    weather_df["day"] = weather_df["Timestamp"].dt.day
    weather_df["hour"] = weather_df["Timestamp"].dt.hour
    
    weather_proxy = weather_df.groupby(["month", "day", "hour"])[
        ["Temperature_C", "Humidity_%", "WindSpeed_mps", "Precipitation_mm"]
    ].mean().reset_index()
    
    # Merge proxy back to main dataframe
    print("Merging weather proxy...")
    df["month"] = df["timestamp"].dt.month
    df["day"] = df["timestamp"].dt.day
    df["hour"] = df["timestamp"].dt.hour
    
    df = df.merge(weather_proxy, on=["month", "day", "hour"], how="left")
    
    # Fill missing weather (e.g. Feb 29 or rare gaps) with forward fill
    df[["Temperature_C", "Humidity_%", "WindSpeed_mps", "Precipitation_mm"]] = \
        df[["Temperature_C", "Humidity_%", "WindSpeed_mps", "Precipitation_mm"]].ffill().bfill()
        
    return df

def create_features(df):
    print("Creating features...")
    df = df.copy()
    
    # Time features
    df["hour"] = df["timestamp"].dt.hour
    df["dayofweek"] = df["timestamp"].dt.dayofweek
    df["month"] = df["timestamp"].dt.month
    df["is_weekend"] = df["dayofweek"].isin([5, 6]).astype(int)
    
    # Cyclical encoding
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["dow_sin"] = np.sin(2 * np.pi * df["dayofweek"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["dayofweek"] / 7)
    
    # Target: 1 hour ahead (4 steps)
    HORIZON = 4
    df["target"] = df.groupby("plant_id")["load_kW"].shift(-HORIZON)
    
    # Lags
    # IMPORTANT: Include lags 1, 2, 3 (recent past) and 4 (1h ago)
    # Also include load_kW (current) in the feature list during training
    # Added lags around 24h (95, 97) and 1 week (672)
    lags = [1, 2, 3, 4, 8, 95, 96, 97, 672] 
    for lag in lags:
        df[f"lag_{lag}"] = df.groupby("plant_id")["load_kW"].shift(lag)
        
    # Rolling stats (24h)
    df["roll_mean_24h"] = df.groupby("plant_id")["load_kW"].transform(lambda x: x.shift(1).rolling(96).mean())
    df["roll_std_24h"] = df.groupby("plant_id")["load_kW"].transform(lambda x: x.shift(1).rolling(96).std())
    
    # Short term rolling (1h = 4 steps)
    df["roll_mean_1h"] = df.groupby("plant_id")["load_kW"].transform(lambda x: x.shift(1).rolling(4).mean())
    df["roll_max_1h"] = df.groupby("plant_id")["load_kW"].transform(lambda x: x.shift(1).rolling(4).max())
    df["roll_min_1h"] = df.groupby("plant_id")["load_kW"].transform(lambda x: x.shift(1).rolling(4).min())
    
    df = df.dropna()
    return df

def global_time_cv(df, features, target, n_folds=3):
    print("Running global time-based CV...")
    ts = df["timestamp"].sort_values().unique()
    if len(ts) < 10:
        return []
    folds = []
    qs = np.linspace(0.6, 0.9, num=n_folds+1)
    for i in range(n_folds):
        q_train = qs[i]
        q_test = qs[i+1]
        t_train = df["timestamp"].quantile(q_train)
        t_test = df["timestamp"].quantile(q_test)
        train_df = df[df["timestamp"] <= t_train]
        test_df = df[(df["timestamp"] > t_train) & (df["timestamp"] <= t_test)]
        if len(train_df) == 0 or len(test_df) == 0:
            continue
        X_train = train_df[features]
        y_train = train_df[target]
        X_test = test_df[features]
        y_test = test_df[target]
        y_pred_base = test_df["load_kW"]
        model = HistGradientBoostingRegressor(
            categorical_features=[features.index("plant_id_enc")],
            random_state=42,
            max_iter=300,
            learning_rate=0.05,
            max_depth=10,
            l2_regularization=0.1
        )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mae_base = mean_absolute_error(y_test, y_pred_base)
        mae_model = mean_absolute_error(y_test, y_pred)
        rmse_model = np.sqrt(mean_squared_error(y_test, y_pred))
        folds.append({
            "fold": i+1,
            "mae_base": float(mae_base),
            "mae_model": float(mae_model),
            "rmse_model": float(rmse_model)
        })
    return folds

def train_eval(df):
    print("Training and evaluating...")

    # Encode plant_id
    enc = OrdinalEncoder()
    df["plant_id_enc"] = enc.fit_transform(df[["plant_id"]])
    
    # Save encoder
    try:
        joblib.dump(enc, os.path.join(MODELS_DIR, "encoder.pkl"))
        print("Encoder saved.")
    except Exception as e:
        print(f"Could not save encoder: {e}")
    
    # Features: Include load_kW (Current Load)
    features = [c for c in df.columns if c not in ["timestamp", "plant_id", "target"]]
    target = "target"
    
    print(f"Features: {features}")
    
    # Split Train/Test per plant (Last 20% is Test)
    df["is_test"] = df.groupby("plant_id")["timestamp"].transform(
        lambda x: x > x.quantile(0.8)
    )
    
    train_df = df[~df["is_test"]]
    test_df = df[df["is_test"]]
    
    print(f"Train size: {len(train_df)} | Test size: {len(test_df)}")
    
    X_train = train_df[features]
    y_train = train_df[target]
    X_test = test_df[features]
    y_test = test_df[target]
    
    # Baseline: Persistence (load at t predicts load at t+4)
    # Since we are predicting t+1h, persistence is assuming load(t+1h) = load(t)
    y_pred_base = test_df["load_kW"]
    
    # Model
    model = HistGradientBoostingRegressor(
        categorical_features=[features.index("plant_id_enc")],
        random_state=42,
        max_iter=500,
        learning_rate=0.05,
        max_depth=10,
        l2_regularization=0.1
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    mae_base = mean_absolute_error(y_test, y_pred_base)
    mae_model = mean_absolute_error(y_test, y_pred)
    rmse_model = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"Overall Baseline MAE: {mae_base:.2f}")
    print(f"Overall Model MAE: {mae_model:.2f} | RMSE: {rmse_model:.2f}")
    
    improvement = mae_base - mae_model
    print(f"Improvement: {improvement:.2f}")

    # Per plant metrics
    test_df["pred"] = y_pred
    test_df["baseline"] = y_pred_base
    test_df["abs_err_model"] = (test_df["target"] - test_df["pred"]).abs()
    test_df["abs_err_base"] = (test_df["target"] - test_df["baseline"]).abs()

    per_plant = test_df.groupby("plant_id")[["abs_err_model", "abs_err_base"]].mean()
    per_plant["improvement"] = per_plant["abs_err_base"] - per_plant["abs_err_model"]
    per_plant = per_plant.sort_values("improvement", ascending=False)

    print("\nTop 5 Improved Plants:")
    print(per_plant.head())

    # Try to plot, but catch error if disk full
    try:
        best_plant = per_plant.index[0]
        plot_sample(test_df[test_df["plant_id"] == best_plant], best_plant)
    except Exception as e:
        print(f"Could not save plot: {e}")

    # Save model and metadata
    try:
        model_path = os.path.join(MODELS_DIR, "model.pkl")
        joblib.dump(model, model_path)
        meta = {
            "features": features,
            "target": target,
            "train_size": int(len(train_df)),
            "test_size": int(len(test_df))
        }
        with open(os.path.join(MODELS_DIR, "metadata.json"), "w") as f:
            json.dump(meta, f)
        print(f"Model saved to {model_path}")
    except Exception as e:
        print(f"Could not save model: {e}")

    # Global time-based CV
    cv_folds = global_time_cv(df, features, target, n_folds=3)
    if cv_folds:
        cv_path = os.path.join(REPORTS_DIR, "evaluation_cv.csv")
        pd.DataFrame(cv_folds).to_csv(cv_path, index=False)
        print(f"CV metrics saved to {cv_path}")
    else:
        print("CV not generated (insufficient data).")

    return per_plant, mae_base, mae_model

def plot_sample(subset, plant_name):
    subset = subset.sort_values("timestamp").iloc[:200]

    plt.figure(figsize=(12, 6))
    plt.plot(subset["timestamp"], subset["target"], label="Real", alpha=0.7)
    plt.plot(subset["timestamp"], subset["pred"], label="Model", alpha=0.7)
    plt.plot(subset["timestamp"], subset["baseline"], label="Persistence", linestyle="--", alpha=0.5)
    plt.title(f"Forecast 1h ahead - {plant_name}")
    plt.legend()
    plt.savefig(os.path.join(FIGURES_DIR, f"forecast_{plant_name}.png"))
    plt.close()

def main():
    df = load_data()
    df = create_features(df)
    per_plant, base, model = train_eval(df)
    
    # Save per plant results
    try:
        per_plant.to_csv(os.path.join(REPORTS_DIR, "per_plant_metrics.csv"))
        print("per_plant_metrics.csv written.")
    except OSError as e:
        print(f"Could not write per_plant_metrics.csv: {e}")
    
    # Report
    try:
        with open(os.path.join(REPORTS_DIR, "model_report.md"), "w") as f:
            f.write("# Industrial Load Forecast Results\n\n")
            f.write(f"**Baseline MAE**: {base:.2f}\n")
            f.write(f"**Model MAE**: {model:.2f}\n")
            f.write(f"**Improvement**: {base - model:.2f} kW\n\n")
            f.write("## Top 10 Plants by Improvement\n")
            f.write(per_plant.head(10).to_markdown())
        print("model_report.md written.")
    except OSError as e:
        print(f"Could not write model_report.md: {e}")

if __name__ == "__main__":
    main()
