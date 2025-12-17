import os
import argparse
import pandas as pd
import numpy as np
import joblib
import json
import warnings

warnings.filterwarnings('ignore')

# --- Config ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
# Assuming the data directory structure is relative to the project root
# industrial_plants_model/../../Hourly Power Load and Climate Data
WEATHER_DATA_PATH = os.path.join(os.path.dirname(BASE_DIR), "Hourly Power Load and Climate Data", "PowerLoad_Dataset.csv")

def load_weather_proxy():
    """Loads and creates the weather proxy from historical data."""
    if not os.path.exists(WEATHER_DATA_PATH):
        raise FileNotFoundError(f"Weather data not found at {WEATHER_DATA_PATH}")
    
    print("Loading Weather Data Proxy...")
    weather_df = pd.read_csv(WEATHER_DATA_PATH)
    weather_df["Timestamp"] = pd.to_datetime(weather_df["Timestamp"])
    
    # Create a proxy by averaging weather by Month, Day, Hour
    weather_df["month"] = weather_df["Timestamp"].dt.month
    weather_df["day"] = weather_df["Timestamp"].dt.day
    weather_df["hour"] = weather_df["Timestamp"].dt.hour
    
    weather_proxy = weather_df.groupby(["month", "day", "hour"])[
        ["Temperature_C", "Humidity_%", "WindSpeed_mps", "Precipitation_mm"]
    ].mean().reset_index()
    
    return weather_proxy

def preprocess_data(df, weather_proxy):
    """Preprocesses the input dataframe for prediction."""
    print("Preprocessing data...")
    df = df.copy()
    
    # Standardize columns
    if "Time stamp" in df.columns:
        df = df.rename(columns={"Time stamp": "timestamp"})
    
    # Ensure timestamps
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d.%m.%Y %H:%M:%S", errors='coerce')
    # Try standard format if specific format fails
    if df["timestamp"].isnull().all():
         df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
         
    df = df.dropna(subset=["timestamp"])
    
    # Clean load_kW if it exists and is string
    if "load_kW" in df.columns and df["load_kW"].dtype == object:
        df["load_kW"] = df["load_kW"].astype(str).str.replace(",", ".").replace("", "0").astype(float)
    
    # Sort
    df = df.sort_values(["plant_id", "timestamp"]).reset_index(drop=True)
    
    # Merge Weather
    print("Merging weather proxy...")
    df["month"] = df["timestamp"].dt.month
    df["day"] = df["timestamp"].dt.day
    df["hour"] = df["timestamp"].dt.hour
    
    df = df.merge(weather_proxy, on=["month", "day", "hour"], how="left")
    
    # Fill missing weather
    df[["Temperature_C", "Humidity_%", "WindSpeed_mps", "Precipitation_mm"]] = \
        df[["Temperature_C", "Humidity_%", "WindSpeed_mps", "Precipitation_mm"]].ffill().bfill()
        
    return df

def create_features(df):
    """Creates features for the model."""
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
    
    # Lags
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
    
    # Drop rows with NaNs created by lags/rolling (cannot predict for start of data)
    # Alternatively, we could keep them and output NaN predictions, but the model will fail.
    # For a robust script, we filter out rows where we can't form features.
    df_clean = df.dropna().copy()
    
    return df_clean

def predict(input_path, output_path=None):
    # Load resources
    model_path = os.path.join(MODELS_DIR, "model.pkl")
    encoder_path = os.path.join(MODELS_DIR, "encoder.pkl")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError("Model file not found. Run train.py first.")
    if not os.path.exists(encoder_path):
        raise FileNotFoundError("Encoder file not found. Run train.py first.")
        
    print("Loading model and encoder...")
    model = joblib.load(model_path)
    encoder = joblib.load(encoder_path)
    
    # Load Data
    print(f"Loading input data from {input_path}...")
    if input_path.endswith('.csv'):
        # Try different separators
        try:
            df = pd.read_csv(input_path, sep=';')
            if "Time stamp" not in df.columns and "timestamp" not in df.columns:
                 df = pd.read_csv(input_path, sep=',')
        except:
             df = pd.read_csv(input_path, sep=',')
    else:
        raise ValueError("Input file must be a CSV.")

    # Process
    weather_proxy = load_weather_proxy()
    df_processed = preprocess_data(df, weather_proxy)
    df_features = create_features(df_processed)
    
    if df_features.empty:
        print("No data available for prediction after feature engineering (not enough history?).")
        return

    # Encode Plant ID
    print("Encoding Plant IDs...")
    # Handle new plant IDs
    known_plants = encoder.categories_[0]
    df_features = df_features[df_features["plant_id"].isin(known_plants)]
    
    if df_features.empty:
        print("No known plant IDs found in input data.")
        return
        
    df_features["plant_id_enc"] = encoder.transform(df_features[["plant_id"]])
    
    # Select features
    # We need to know the exact feature order used in training.
    # Since we don't have metadata.json with feature list easily accessible (it is saved in train.py but I didn't read it here yet),
    # I should load it.
    with open(os.path.join(MODELS_DIR, "metadata.json"), "r") as f:
        meta = json.load(f)
    feature_cols = meta["features"]
    
    X = df_features[feature_cols]
    
    print("Predicting...")
    predictions = model.predict(X)
    
    df_features["predicted_load_kW_1h_ahead"] = predictions
    
    # Save
    if output_path is None:
        output_path = input_path.replace(".csv", "_predictions.csv")
    
    # Output columns: timestamp, plant_id, predicted_load
    output_df = df_features[["timestamp", "plant_id", "load_kW", "predicted_load_kW_1h_ahead"]]
    output_df.to_csv(output_path, index=False)
    print(f"Predictions saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict 1h ahead load for industrial plants.")
    parser.add_argument("input_file", help="Path to input CSV file")
    parser.add_argument("--output", help="Path to output CSV file", default=None)
    
    args = parser.parse_args()
    
    predict(args.input_file, args.output)
