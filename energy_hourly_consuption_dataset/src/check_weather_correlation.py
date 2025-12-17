import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def main():
    # Load integrated data
    path = os.path.join('data', 'processed', 'pjm_integrated.csv')
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    df = pd.read_csv(path)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    
    # Filter for 2018 where we have weather data
    df_2018 = df[df['Datetime'].dt.year == 2018].copy()
    
    if df_2018.empty:
        print("No data for 2018 found.")
        return

    # Check for weather columns
    weather_cols = ['temp_c', 'wind_ms', 'irradiance_wm2']
    available_weather = [c for c in weather_cols if c in df_2018.columns]
    
    if not available_weather:
        print("No weather columns found.")
        return

    print(f"Analyzing correlation for 2018 with weather cols: {available_weather}")
    
    # Select numeric columns for correlation
    # We focus on PJM_Load and AEP vs Weather
    target_cols = ['PJM_Load', 'AEP']
    cols_to_corr = [c for c in target_cols if c in df_2018.columns] + available_weather
    
    corr = df_2018[cols_to_corr].corr()
    print("\nCorrelation Matrix (2018):")
    print(corr)
    
    # Save correlation matrix
    os.makedirs(os.path.join('reports', 'metrics'), exist_ok=True)
    corr.to_csv(os.path.join('reports', 'metrics', 'weather_correlation_2018.csv'))
    print("\nSaved correlation matrix to reports/metrics/weather_correlation_2018.csv")

if __name__ == '__main__':
    main()
