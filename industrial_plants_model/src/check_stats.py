
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "Load profile data of 50 industrial plants")

def check_data():
    df_2016 = pd.read_csv(os.path.join(DATA_DIR, "LoadProfile_20IPs_2016.csv"), sep=";", header=1, low_memory=False)
    df_2017 = pd.read_csv(os.path.join(DATA_DIR, "LoadProfile_30IPs_2017.csv"), sep=";", header=1, low_memory=False)
    
    # Clean 2016
    cols_16 = [c for c in df_2016.columns if c != "Time stamp"]
    for c in cols_16:
        if df_2016[c].dtype == object:
            df_2016[c] = df_2016[c].astype(str).str.replace(",", ".").replace("", "0").astype(float)
            
    # Clean 2017
    cols_17 = [c for c in df_2017.columns if c != "Time stamp"]
    for c in cols_17:
        if df_2017[c].dtype == object:
            df_2017[c] = df_2017[c].astype(str).str.replace(",", ".").replace("", "0").astype(float)
            
    print("2016 Stats:")
    print(df_2016[cols_16].describe().T[["mean", "min", "max"]])
    
    print("\n2017 Stats:")
    print(df_2017[cols_17].describe().T[["mean", "min", "max"]])

if __name__ == "__main__":
    check_data()
