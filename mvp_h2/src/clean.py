import pandas as pd
import numpy as np

def parse_timestamp(df, col):
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

def to_numeric(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def impute_missing(df, cols, strategy="median"):
    for c in cols:
        if c in df.columns:
            if strategy == "median":
                df[c] = df[c].fillna(df[c].median())
            elif strategy == "mean":
                df[c] = df[c].fillna(df[c].mean())
            elif strategy == "zero":
                df[c] = df[c].fillna(0.0)
    return df

def iqr_cap(df, cols):
    for c in cols:
        if c in df.columns:
            q1 = df[c].quantile(0.25)
            q3 = df[c].quantile(0.75)
            iqr = q3 - q1
            low = q1 - 1.5 * iqr
            high = q3 + 1.5 * iqr
            df[c] = np.clip(df[c], low, high)
    return df

def run(df, numeric_columns, timestamp_column, impute_strategy="median", outlier_method="iqr_cap"):
    df = parse_timestamp(df, timestamp_column)
    df = to_numeric(df, numeric_columns)
    df = impute_missing(df, numeric_columns, strategy=impute_strategy)
    if outlier_method == "iqr_cap":
        df = iqr_cap(df, numeric_columns)
    return df
