
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
import warnings

warnings.filterwarnings('ignore')

# --- Config ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = BASE_DIR # The csvs are in the root of this folder
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")

os.makedirs(FIGURES_DIR, exist_ok=True)

def load_data():
    print("Loading energy data...")
    df_energy = pd.read_csv(os.path.join(DATA_DIR, "energy_dataset.csv"))
    
    print("Loading weather data...")
    df_weather = pd.read_csv(os.path.join(DATA_DIR, "weather_features.csv"))
    
    return df_energy, df_weather

def preprocess(df_energy, df_weather):
    print("Preprocessing...")
    
    # Time parsing
    # Energy time is "2015-01-01 00:00:00+01:00" -> convert to UTC or just datetime
    df_energy["time"] = pd.to_datetime(df_energy["time"], utc=True)
    df_energy = df_energy.set_index("time").sort_index()
    
    # Weather time "dt_iso"
    df_weather["dt_iso"] = pd.to_datetime(df_weather["dt_iso"], utc=True)
    
    # Aggregate weather across cities (mean)
    # This gives us a "general" weather signal for the region
    print("Aggregating weather data...")
    weather_numeric = df_weather.select_dtypes(include=[np.number])
    weather_numeric["dt_iso"] = df_weather["dt_iso"]
    df_weather_agg = weather_numeric.groupby("dt_iso").mean()
    
    # Merge
    print("Merging datasets...")
    # We want to predict 'total load actual'
    target_col = "total load actual"
    
    # Keep only relevant columns from energy
    # We might want generation as features? Or just load history?
    # Usually forecasting load relies on past load + weather + time.
    # Future generation is unknown (unless forecasted).
    # The dataset has 'total load forecast', which is a strong baseline to beat or use as feature.
    # Let's try to build a model that uses weather + past load, and maybe compare to 'total load forecast'.
    
    cols_to_keep = [target_col]
    df_merged = df_energy[cols_to_keep].join(df_weather_agg, how="inner")
    
    # Interpolate missing
    df_merged = df_merged.interpolate(method="time")
    df_merged = df_merged.dropna()
    
    return df_merged

def create_features(df):
    print("Creating features...")
    df = df.copy()
    
    # Time features (from index)
    df["hour"] = df.index.hour
    df["dayofweek"] = df.index.dayofweek
    df["month"] = df.index.month
    df["is_weekend"] = df["dayofweek"].isin([5, 6]).astype(int)
    
    # Cyclical
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    
    # Lags of Target
    # Predict 1h ahead.
    # Features available at T: Load(T), Load(T-1)...
    # Target: Load(T+1) ??
    # Usually "Forecasting" means at time T we want to know T+1.
    # So we shift target backwards? Or shift features forward?
    # Let's align: Row T contains Features(T) and Target(T+1).
    
    target_col = "total load actual"
    
    # We want to predict t+1. 
    # So at row t, we have weather(t+1) (forecast)?? 
    # In this dataset, weather is historical. 
    # Assuming we have perfect weather forecast (or using actuals as proxy for forecast),
    # we can use Weather(T) to predict Load(T).
    # Load is instantaneous. 
    # Let's predict Load(T) using Weather(T) and Load(T-1, T-2...).
    # This is a standard setup.
    
    # Create Lags
    lags = [1, 2, 3, 24, 168] # 1h, 2h, 3h, 24h, 1 week
    for lag in lags:
        df[f"lag_{lag}"] = df[target_col].shift(lag)
        
    # Rolling stats
    df["roll_mean_24"] = df[target_col].shift(1).rolling(24).mean()
    
    df = df.dropna()
    
    return df

def train_eval(df):
    print("Training and evaluating...")
    
    target_col = "total load actual"
    features = [c for c in df.columns if c != target_col]
    
    # Split
    # Last 20% test
    split_idx = int(len(df) * 0.8)
    
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    X_train = train_df[features]
    y_train = train_df[target_col]
    X_test = test_df[features]
    y_test = test_df[target_col]
    
    # Baseline: Persistence (Lag 1) -> Predict T using T-1
    # Since we are predicting Load(T), persistence is Load(T-1).
    # We already have lag_1 feature.
    y_pred_base = X_test["lag_1"]
    
    # Model
    model = HistGradientBoostingRegressor(random_state=42, max_iter=200)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # Metrics
    mae_base = mean_absolute_error(y_test, y_pred_base)
    mae_model = mean_absolute_error(y_test, y_pred)
    rmse_model = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"Baseline MAE: {mae_base:.2f}")
    print(f"Model MAE: {mae_model:.2f} | RMSE: {rmse_model:.2f}")
    print(f"Improvement: {mae_base - mae_model:.2f}")
    
    # Plot
    try:
        plot_forecast(y_test, y_pred, y_pred_base)
    except Exception as e:
        print(f"Could not save plot: {e}")
        
    return mae_base, mae_model

def plot_forecast(y_test, y_pred, y_base):
    # Plot first week of test
    limit = 168
    
    plt.figure(figsize=(12, 6))
    plt.plot(y_test.index[:limit], y_test.iloc[:limit], label="Actual", alpha=0.8)
    plt.plot(y_test.index[:limit], y_pred[:limit], label="Model", alpha=0.8)
    plt.plot(y_test.index[:limit], y_base[:limit], label="Persistence", linestyle="--", alpha=0.5)
    
    plt.title("Energy Load Forecast (1h ahead) - First Week of Test")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "energy_forecast.png"))
    plt.close()

def main():
    df_energy, df_weather = load_data()
    df = preprocess(df_energy, df_weather)
    df = create_features(df)
    base, model = train_eval(df)
    
    # Save Report
    with open(os.path.join(REPORTS_DIR, "energy_model_report.md"), "w") as f:
        f.write("# Energy Load Forecast Results\n\n")
        f.write(f"- **Baseline MAE**: {base:.2f}\n")
        f.write(f"- **Model MAE**: {model:.2f}\n")
        f.write(f"- **Improvement**: {base - model:.2f} MW\n\n")
        f.write("![Forecast](figures/energy_forecast.png)\n")

if __name__ == "__main__":
    main()
