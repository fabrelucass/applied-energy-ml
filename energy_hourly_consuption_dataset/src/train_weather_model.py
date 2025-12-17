import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pandas.tseries.holiday import USFederalHolidayCalendar

def load_data(path):
    df = pd.read_csv(path)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    return df

def add_features(df, weather=False):
    df = df.copy()
    df['hora'] = df['Datetime'].dt.hour
    df['dia_semana'] = df['Datetime'].dt.dayofweek
    df['mes'] = df['Datetime'].dt.month
    df['ano'] = df['Datetime'].dt.year
    
    # Lags
    df['lag1'] = df['AEP'].shift(1)
    df['lag24'] = df['AEP'].shift(24)
    
    # Weekend/Holiday
    df['fim_semana'] = df['dia_semana'].isin([5,6]).astype(int)
    cal = USFederalHolidayCalendar()
    hdays = cal.holidays(start=str(df['Datetime'].min().date()), end=str(df['Datetime'].max().date()))
    df['feriado'] = df['Datetime'].dt.normalize().isin(hdays).astype(int)
    
    features = ['hora', 'dia_semana', 'mes', 'lag1', 'lag24', 'fim_semana', 'feriado']
    
    if weather:
        # Weather features (lagged to be realistic? or actuals if forecast assumed perfect?)
        # For this MVP, we use actuals (simulating perfect forecast) or we could lag them.
        # Let's use actuals as a "potential gain" upper bound.
        weather_cols = ['temp_c', 'wind_ms', 'irradiance_wm2']
        # Fill missing weather (if any) with ffill
        for c in weather_cols:
            if c in df.columns:
                df[c] = df[c].ffill()
                features.append(c)
            else:
                print(f"Warning: {c} not in dataframe")
                
    return df, features

def fit_predict(df, features, train_years, test_year):
    # Prepare X, y
    data = df.dropna(subset=features + ['AEP'])
    
    train_mask = data['ano'].isin(train_years)
    test_mask = data['ano'] == test_year
    
    X_train = data.loc[train_mask, features].values
    y_train = data.loc[train_mask, 'AEP'].values
    
    X_test = data.loc[test_mask, features].values
    y_test = data.loc[test_mask, 'AEP'].values
    
    if len(X_train) == 0 or len(X_test) == 0:
        return None, None, None
    
    # Linear Regression (using numpy for speed/no sklearn dependency if preferred, matching mvp_energy.py)
    # Add intercept
    X_train_b = np.c_[np.ones(len(X_train)), X_train]
    X_test_b = np.c_[np.ones(len(X_test)), X_test]
    
    # Solve
    XtX = X_train_b.T @ X_train_b
    Xty = X_train_b.T @ y_train
    # Add small regularization for stability
    XtX = XtX + 1e-5 * np.eye(XtX.shape[0])
    beta = np.linalg.pinv(XtX) @ Xty
    
    y_pred = X_test_b @ beta
    
    return y_test, y_pred, beta

def metrics(y_true, y_pred):
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred)**2))
    return mae, rmse

def main():
    path = os.path.join('data', 'processed', 'pjm_integrated.csv')
    if not os.path.exists(path):
        print("Data not found.")
        return
        
    df = load_data(path)
    print(f"Total rows: {len(df)}")
    print(f"Years: {df['Datetime'].dt.year.unique()}")
    
    # Focus on 2016-2018
    df = df[df['Datetime'].dt.year.isin([2016, 2017, 2018])].copy()
    print(f"Rows after filter (2016-2018): {len(df)}")
    
    # 1. Base Model (v2 equivalent: lags + calendar + holidays)
    df_base, feats_base = add_features(df, weather=False)
    y_true, y_pred_base, _ = fit_predict(df_base, feats_base, [2016, 2017], 2018)
    
    if y_true is None:
        print("Not enough data for split.")
        return
        
    mae_base, rmse_base = metrics(y_true, y_pred_base)
    print(f"Base Model (2018 Test): MAE={mae_base:.2f}, RMSE={rmse_base:.2f}")
    
    # 2. Weather Model
    df_weather, feats_weather = add_features(df, weather=True)
    y_true_w, y_pred_w, _ = fit_predict(df_weather, feats_weather, [2016, 2017], 2018)
    
    mae_w, rmse_w = metrics(y_true_w, y_pred_w)
    print(f"Weather Model (2018 Test): MAE={mae_w:.2f}, RMSE={rmse_w:.2f}")
    
    # Improvements
    imp_mae = mae_base - mae_w
    imp_rmse = rmse_base - rmse_w
    print(f"Improvement: MAE -{imp_mae:.2f}, RMSE -{imp_rmse:.2f}")
    
    # Plot comparison
    res_base = np.abs(y_true - y_pred_base)
    res_w = np.abs(y_true_w - y_pred_w)
    
    # Use df_base for datetime indexing since it has the 'ano' column
    # Also align lengths carefully
    test_dt = df_base.loc[df_base['ano'] == 2018, 'Datetime'].iloc[-len(y_true):].values
    
    results = pd.DataFrame({
        'Datetime': test_dt,
        'Base_Err': res_base,
        'Weather_Err': res_w
    })
    results['Hour'] = pd.to_datetime(results['Datetime']).dt.hour
    
    hourly_mae = results.groupby('Hour')[['Base_Err', 'Weather_Err']].mean()
    
    plt.figure(figsize=(10, 6))
    plt.plot(hourly_mae.index, hourly_mae['Base_Err'], label='Base Model', marker='o')
    plt.plot(hourly_mae.index, hourly_mae['Weather_Err'], label='Weather Model', marker='x')
    plt.title('MAE by Hour: Base vs Weather Model (2018)')
    plt.xlabel('Hour of Day')
    plt.ylabel('MAE (MW)')
    plt.legend()
    plt.grid(True)
    
    out_path = os.path.join('reports', 'figures', 'weather_model_comparison.png')
    plt.savefig(out_path)
    print(f"Comparison plot saved to {out_path}")

if __name__ == '__main__':
    main()
