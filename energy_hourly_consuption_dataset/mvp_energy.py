"""
MVP Analítico – Consumo Horário de Energia (PJM)

Etapas da análise:
1) Ingestão e limpeza: leitura dos CSVs por zona e padronização de `Datetime` e tipos
2) Enriquecimento temporal: criação de variáveis de calendário (hora, dia, mês, ano, estação)
3) EDA operacional: histogramas, curvas por hora e por dia da semana
4) Métricas de operação: fator de carga diário e relação pico vs média
5) Modelagem básica: baseline lag-1 e regressão linear com features simples
6) Relato: consolidação das evidências e métricas em `reports/mvp_report.md`
"""

import os
import math
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pandas.tseries.holiday import USFederalHolidayCalendar

def load_series(path, value_col, agg='mean'):
    """
    Leitura e preparação de uma série horária:
    - Lê CSV em `path`
    - Converte `Datetime` para datetime e ordena temporalmente
    - Garante tipo numérico para `value_col`
    - Agrega duplicidades por `Datetime` usando `agg` (mean, max, etc.)
    - Retorna DataFrame pronto para análise
    """
    df = pd.read_csv(path, low_memory=False)
    df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
    df = df.dropna(subset=['Datetime'])
    df = df.sort_values('Datetime')
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    if df['Datetime'].duplicated().any():
        df = df.groupby('Datetime', as_index=False)[value_col].agg(agg)
    return df


def add_time_features(df):
    """
    Enriquecimento temporal:
    - Extrai `hora`, `dia_semana`, `mes`, `ano`
    - Define `estacao` (inverno, primavera, verao, outono) com base no mês
    - Adiciona flags `fim_semana` e `dia_util`
    - Retorna DataFrame com features adicionadas
    """
    df['hora'] = df['Datetime'].dt.hour
    df['dia_semana'] = df['Datetime'].dt.dayofweek
    df['mes'] = df['Datetime'].dt.month
    df['ano'] = df['Datetime'].dt.year
    m = df['mes']
    season = np.where(m.isin([12,1,2]), 'inverno',
             np.where(m.isin([3,4,5]), 'primavera',
             np.where(m.isin([6,7,8]), 'verao', 'outono')))
    df['estacao'] = season
    df['fim_semana'] = df['dia_semana'].isin([5,6])
    df['dia_util'] = ~df['fim_semana']
    cal = USFederalHolidayCalendar()
    hdays = cal.holidays(start=str(df['Datetime'].min().date()), end=str(df['Datetime'].max().date()))
    df['feriado'] = df['Datetime'].dt.normalize().isin(hdays)
    return df


def ensure_dir(d):
    """
    Cria diretório `d` se não existir
    """
    os.makedirs(d, exist_ok=True)


def plot_histogram(df, value_col, out_path, show=False):
    """
    Histograma com KDE para coluna numérica:
    - Salva figura em `out_path`
    """
    plt.figure(figsize=(8,5))
    sns.histplot(df[value_col].dropna(), bins=40, kde=True)
    plt.title(f"Histograma {value_col}")
    plt.xlabel(value_col)
    plt.tight_layout()
    plt.savefig(out_path)
    if show:
        plt.show()
    plt.close()


def hourly_curve_year(df, value_col, year, out_path, show=False):
    """
    Curva média por hora para um `year` específico:
    - Agrupa por `hora` e calcula média de `value_col`
    - Gera figura e retorna a série agregada
    """
    d = df[df['ano'] == year]
    g = d.groupby('hora')[value_col].mean()
    plt.figure(figsize=(9,5))
    sns.lineplot(x=g.index, y=g.values)
    plt.title(f"Curva média por hora ({value_col}) em {year}")
    plt.xlabel("Hora do dia")
    plt.ylabel("MW médio")
    plt.tight_layout()
    plt.savefig(out_path)
    if show:
        plt.show()
    plt.close()
    return g


def dow_curve(df, value_col, out_path, show=False):
    """
    Curva média por dia da semana:
    - Agrupa por `dia_semana` e calcula média de `value_col`
    - Gera figura e retorna a série agregada
    """
    g = df.groupby('dia_semana')[value_col].mean()
    plt.figure(figsize=(9,5))
    sns.lineplot(x=g.index, y=g.values)
    plt.title(f"Curva média por dia da semana ({value_col})")
    plt.xlabel("Dia da semana (0=Seg)")
    plt.ylabel("MW médio")
    plt.tight_layout()
    plt.savefig(out_path)
    if show:
        plt.show()
    plt.close()
    return g


def seasonal_hourly_diff(df, value_col):
    """
    Top horas por estação:
    - Calcula média por (`estacao`, `hora`)
    - Retorna top-3 de verão e de inverno
    """
    g = df.groupby(['estacao','hora'])[value_col].mean().reset_index()
    verao = g[g['estacao']=='verao']
    inverno = g[g['estacao']=='inverno']
    if not verao.empty and not inverno.empty:
        m_verao = verao.sort_values(value_col, ascending=False).head(3)
        m_inverno = inverno.sort_values(value_col, ascending=False).head(3)
    else:
        m_verao = pd.DataFrame()
        m_inverno = pd.DataFrame()
    return m_verao, m_inverno


def daily_load_factor(df, value_col):
    """
    Fator de carga diário:
    - Reamostra por dia (`D`)
    - Calcula `media`, `pico` e `fator = media/pico`
    - Retorna DataFrame com colunas: data, media, pico, fator
    """
    d = df.set_index('Datetime')[value_col].resample('D')
    mean = d.mean()
    peak = d.max()
    fac = (mean/peak).rename('fator')
    out = pd.concat([mean.rename('media'), peak.rename('pico'), fac], axis=1).dropna()
    out = out.reset_index().rename(columns={'Datetime':'data'})
    return out


def plot_peak_vs_mean(daily_df, out_path, show=False):
    """
    Dispersão entre média diária e pico diário:
    - Ajuda a visualizar correlação e dispersão de operação
    """
    plt.figure(figsize=(7,6))
    sns.scatterplot(x=daily_df['media'], y=daily_df['pico'])
    plt.title("Relação pico diário vs média diária")
    plt.xlabel("Média (MW)")
    plt.ylabel("Pico (MW)")
    plt.tight_layout()
    plt.savefig(out_path)
    if show:
        plt.show()
    plt.close()


def build_features(df, value_col):
    """
    Construção de features para modelo:
    - Adiciona lags (1h, 24h) e calendário (hora, dia, mês)
    - Monta matriz X com termo de intercepto e vetor y
    - Retorna índice temporal, X e y alinhados
    """
    df = df.copy()
    df['lag1'] = df[value_col].shift(1)
    df['lag24'] = df[value_col].shift(24)
    X = df[['hora','dia_semana','mes','lag1','lag24']]
    y = df[value_col]
    m = pd.concat([df[['Datetime']], X, y], axis=1).dropna()
    X = m[['hora','dia_semana','mes','lag1','lag24']].values.astype(float)
    y = m[value_col].values.astype(float)
    X = np.concatenate([np.ones((X.shape[0],1)), X], axis=1)
    return m[['Datetime']], X, y


def build_features_weekend(df, value_col):
    """
    Versão estendida de features:
    - Inclui `fim_semana` e `feriado` como flags adicionais
    """
    df = df.copy()
    df['lag1'] = df[value_col].shift(1)
    df['lag24'] = df[value_col].shift(24)
    df['fim_semana_flag'] = df['fim_semana'].astype(int)
    df['feriado_flag'] = df.get('feriado', False)
    df['feriado_flag'] = df['feriado_flag'].astype(int)
    X = df[['hora','dia_semana','mes','lag1','lag24','fim_semana_flag','feriado_flag']]
    y = df[value_col]
    m = pd.concat([df[['Datetime']], X, y], axis=1).dropna()
    X = m[['hora','dia_semana','mes','lag1','lag24','fim_semana_flag','feriado_flag']].values.astype(float)
    y = m[value_col].values.astype(float)
    X = np.concatenate([np.ones((X.shape[0],1)), X], axis=1)
    return m[['Datetime']], X, y


def split_train_test(df_time, X, y):
    """
    Split temporal por último ano:
    - Treino: anos anteriores ao último
    - Teste: último ano
    - Retorna último ano e conjuntos de treino/teste
    """
    years = df_time['Datetime'].dt.year
    last_year = int(years.max())
    train_idx = years != last_year
    test_idx = years == last_year
    X_train = X[train_idx.values]
    y_train = y[train_idx.values]
    X_test = X[test_idx.values]
    y_test = y[test_idx.values]
    return last_year, X_train, y_train, X_test, y_test


def time_series_cv(df_time, X, y, n_splits=3, mode='expanding'):
    """
    Validação temporal com janelas:
    - `expanding`: treina em anos até k-1 e testa em ano k
    - `rolling`: treina só no ano k-1 e testa em ano k
    - Retorna lista de dicts com ano de teste e métricas MAE/RMSE
    """
    yrs = sorted(df_time['Datetime'].dt.year.unique())
    if len(yrs) < 2:
        return []
    splits = []
    end = len(yrs)
    start = max(1, end - n_splits)
    for i in range(start, end):
        test_year = yrs[i]
        if mode == 'expanding':
            train_years = yrs[:i]
        else:
            train_years = [yrs[i-1]]
        tr_mask = df_time['Datetime'].dt.year.isin(train_years).values
        te_mask = (df_time['Datetime'].dt.year == test_year).values
        X_tr, y_tr = X[tr_mask], y[tr_mask]
        X_te, y_te = X[te_mask], y[te_mask]
        if len(y_tr) == 0 or len(y_te) == 0:
            continue
        beta = fit_linear_regression(X_tr, y_tr)
        y_hat = predict_linear_regression(X_te, beta)
        mae, rmse = metrics(y_te, y_hat)
        splits.append({'test_year': int(test_year), 'mae': float(mae), 'rmse': float(rmse)})
    return splits


def fit_linear_regression(X, y):
    """
    Regressão linear via solução de mínimos quadrados:
    - Usa pseudo-inversa de X^T X
    - Retorna vetor de coeficientes
    """
    XtX = X.T @ X
    Xty = X.T @ y
    beta = np.linalg.pinv(XtX) @ Xty
    return beta


def predict_linear_regression(X, beta):
    """
    Predição linear: y_hat = X @ beta
    """
    return X @ beta


def metrics(y_true, y_pred):
    """
    Métricas de erro:
    - MAE: erro absoluto médio
    - RMSE: raiz do erro quadrático médio
    """
    dif = y_true - y_pred
    mae = float(np.mean(np.abs(dif)))
    rmse = float(np.sqrt(np.mean(dif**2)))
    return mae, rmse


def baseline_prev(df, value_col):
    """
    Baseline de previsão lag-1:
    - Compara valor atual com valor da hora anterior
    - Retorna MAE e RMSE do baseline
    """
    df = df.copy()
    df['y_true'] = df[value_col]
    df['y_pred'] = df[value_col].shift(1)
    m = df.dropna()
    y_true = m['y_true'].values.astype(float)
    y_pred = m['y_pred'].values.astype(float)
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred)**2)))
    return mae, rmse


def plot_residuals(y_true, y_pred, df_time, out_hist_path, out_hour_path, show=False):
    """
    Visualização de resíduos:
    - Histograma de resíduos
    - Erro absoluto médio por hora do dia
    """
    res = y_true - y_pred
    plt.figure(figsize=(8,5))
    sns.histplot(res, bins=40, kde=True)
    plt.title("Histograma de resíduos (teste)")
    plt.xlabel("Resíduo (MW)")
    plt.tight_layout()
    plt.savefig(out_hist_path)
    if show:
        plt.show()
    plt.close()
    d = pd.DataFrame({'Datetime': df_time['Datetime'].values[-len(res):], 'res': res})
    d['hora'] = pd.to_datetime(d['Datetime']).dt.hour
    g = d.groupby('hora')['res'].apply(lambda s: np.mean(np.abs(s)))
    plt.figure(figsize=(9,5))
    sns.lineplot(x=g.index, y=g.values)
    plt.title("Erro absoluto médio por hora (teste)")
    plt.xlabel("Hora do dia")
    plt.ylabel("Erro absoluto médio (MW)")
    plt.tight_layout()
    plt.savefig(out_hour_path)
    if show:
        plt.show()
    plt.close()


def plot_residuals_holiday_comparison(y_true, y_pred, df_time_with_flags, out_path, show=False):
    """
    Comparação de erro por hora entre feriado e não feriado:
    - Plota duas curvas (feriado vs não feriado) de erro absoluto médio por hora
    """
    res = y_true - y_pred
    d = pd.DataFrame({'Datetime': df_time_with_flags['Datetime'].values[-len(res):], 'res': res})
    d = pd.merge(d, df_time_with_flags[['Datetime', 'feriado']], on='Datetime', how='left')
    d['hora'] = pd.to_datetime(d['Datetime']).dt.hour
    g_h = d[d['feriado'] == True].groupby('hora')['res'].apply(lambda s: np.mean(np.abs(s)))
    g_nh = d[d['feriado'] != True].groupby('hora')['res'].apply(lambda s: np.mean(np.abs(s)))
    plt.figure(figsize=(9,5))
    sns.lineplot(x=g_h.index, y=g_h.values, label='Feriado')
    sns.lineplot(x=g_nh.index, y=g_nh.values, label='Não feriado')
    plt.title("Erro absoluto médio por hora — feriado vs não feriado (teste)")
    plt.xlabel("Hora do dia")
    plt.ylabel("Erro absoluto médio (MW)")
    plt.tight_layout()
    plt.savefig(out_path)
    if show:
        plt.show()
    plt.close()

def plot_residuals_model_compare(y_true_v1, y_pred_v1, df_time_v1, y_true_v2, y_pred_v2, df_time_v2, out_path, show=False):
    res1 = y_true_v1 - y_pred_v1
    d1 = pd.DataFrame({'Datetime': df_time_v1['Datetime'].values[-len(res1):], 'res': res1})
    d1['hora'] = pd.to_datetime(d1['Datetime']).dt.hour
    g1 = d1.groupby('hora')['res'].apply(lambda s: np.mean(np.abs(s)))
    res2 = y_true_v2 - y_pred_v2
    d2 = pd.DataFrame({'Datetime': df_time_v2['Datetime'].values[-len(res2):], 'res': res2})
    d2['hora'] = pd.to_datetime(d2['Datetime']).dt.hour
    g2 = d2.groupby('hora')['res'].apply(lambda s: np.mean(np.abs(s)))
    plt.figure(figsize=(9,5))
    sns.lineplot(x=g1.index, y=g1.values, label='Linear v1')
    sns.lineplot(x=g2.index, y=g2.values, label='Linear v2')
    plt.title("Erro absoluto médio por hora — comparação de modelos (teste)")
    plt.xlabel("Hora do dia")
    plt.ylabel("Erro absoluto médio (MW)")
    plt.tight_layout()
    plt.savefig(out_path)
    if show:
        plt.show()
    plt.close()

def hourly_error_table(y_true_v1, y_pred_v1, df_time_v1, y_true_v2, y_pred_v2, df_time_v2, top_n=5):
    res1 = y_true_v1 - y_pred_v1
    d1 = pd.DataFrame({'Datetime': df_time_v1['Datetime'].values[-len(res1):], 'res': res1})
    d1['hora'] = pd.to_datetime(d1['Datetime']).dt.hour
    g1 = d1.groupby('hora')['res'].apply(lambda s: np.mean(np.abs(s))).rename('mae_v1')
    res2 = y_true_v2 - y_pred_v2
    d2 = pd.DataFrame({'Datetime': df_time_v2['Datetime'].values[-len(res2):], 'res': res2})
    d2['hora'] = pd.to_datetime(d2['Datetime']).dt.hour
    g2 = d2.groupby('hora')['res'].apply(lambda s: np.mean(np.abs(s))).rename('mae_v2')
    t = pd.concat([g1, g2], axis=1)
    t['improvement'] = t['mae_v1'] - t['mae_v2']
    t = t.reset_index().rename(columns={'index':'hora'})
    t = t.sort_values('improvement', ascending=False)
    return t.head(top_n), t

def plot_hourly_improvement_bar(hourly_df, out_path, show=False):
    d = hourly_df.sort_values('hora').copy()
    cols = ['#d62728' if v < 0 else '#2ca02c' for v in d['improvement']]
    plt.figure(figsize=(10,5))
    plt.bar(d['hora'], d['improvement'], color=cols)
    plt.title("Ganho por hora (MAE_v1 − MAE_v2)")
    plt.xlabel("Hora do dia")
    plt.ylabel("Ganho de MAE (positivo = v2 melhor)")
    plt.tight_layout()
    plt.savefig(out_path)
    if show:
        plt.show()
    plt.close()


def write_report(path, context, aep_hist, pjm_hist, aep_hour_curve, pjm_hour_curve, aep_dow_curve, pjm_dow_curve, lf_table_path, lf_worst, peak_mean_plot, base_mae, base_rmse, lin_mae, lin_rmse, last_year, verao_top, inverno_top, cv_exp=None, cv_roll=None, resid_hist=None, resid_hour=None, lin2_mae=None, lin2_rmse=None, cv_exp2=None, cv_roll2=None, resid_hist2=None, resid_hour2=None, model_cmp_fig=None, hourly_cmp_top=None, hourly_cmp_csv=None, hourly_cmp_worst=None, improvement_fig=None):
    """
    Consolidação em relatório:
    - Introdução, EDA, métricas operacionais, modelos e próximos passos
    - Salva `reports/mvp_report.md` com links para figuras
    """
    lines = []
    lines.append("# MVP Analítico: Consumo Horário de Energia (PJM)")
    lines.append("")
    lines.append(f"Contexto: {context}")
    lines.append("")
    lines.append("## Sumário Executivo")
    lines.append("")
    lines.append("| Modelo | MAE (teste) | RMSE (teste) |")
    lines.append("|---|---:|---:|")
    lines.append(f"| Baseline lag‑1 | {base_mae:.2f} | {base_rmse:.2f} |")
    lines.append(f"| Linear v1 | {lin_mae:.2f} | {lin_rmse:.2f} |")
    if lin2_mae is not None and lin2_rmse is not None:
        lines.append(f"| Linear v2 | {lin2_mae:.2f} | {lin2_rmse:.2f} |")
    lines.append("")
    lines.append("## Introdução")
    lines.append("Entender padrões básicos (hora, dia, estação) e identificar picos/vales para flexibilidade.")
    lines.append("")
    lines.append("## Carregamento e preparação")
    lines.append("Arquivos: AEP_hourly.csv e PJM_Load_hourly.csv. Conversão de `Datetime` e criação de hora, dia da semana, mês, ano, estação.")
    lines.append("")
    lines.append("## EDA básica")
    lines.append("Histogramas:")
    lines.append(f"- `{os.path.basename(aep_hist)}`")
    lines.append(f"- `{os.path.basename(pjm_hist)}`")
    lines.append("Curvas médias por hora (ano de teste):")
    lines.append(f"- AEP: `{os.path.basename(aep_hour_curve)}`")
    lines.append(f"- PJM_Load: `{os.path.basename(pjm_hour_curve)}`")
    lines.append("Curva média por dia da semana:")
    lines.append(f"- AEP: `{os.path.basename(aep_dow_curve)}`")
    lines.append(f"- PJM_Load: `{os.path.basename(pjm_dow_curve)}`")
    if not verao_top.empty:
        vn = verao_top.columns[-1]
        lines.append("Top horas de verão (AEP):")
        for _, r in verao_top.iterrows():
            lines.append(f"- hora {int(r['hora'])}: {float(r[vn]):.1f} MW")
    if not inverno_top.empty:
        vn = inverno_top.columns[-1]
        lines.append("Top horas de inverno (AEP):")
        for _, r in inverno_top.iterrows():
            lines.append(f"- hora {int(r['hora'])}: {float(r[vn]):.1f} MW")
    lines.append("")
    lines.append("## Métricas simples de fator de carga")
    lines.append(f"Tabela salva: `{os.path.basename(lf_table_path)}`")
    lines.append("Dias com menor fator de carga:")
    for _, r in lf_worst.iterrows():
        lines.append(f"- {pd.to_datetime(r['data']).date()} fator {float(r['fator']):.3f} média {float(r['media']):.1f} pico {float(r['pico']):.1f}")
    lines.append(f"Relação pico vs média: `{os.path.basename(peak_mean_plot)}`")
    lines.append("")
    lines.append("## Modelo de previsão básico (AEP)")
    lines.append(f"Período de teste: {last_year}")
    lines.append(f"Baseline (lag 1h): MAE={base_mae:.2f} RMSE={base_rmse:.2f}")
    lines.append(f"Regressão Linear (hora, dia_semana, mês, lag1, lag24): MAE={lin_mae:.2f} RMSE={lin_rmse:.2f}")
    lines.append("")
    if lin2_mae is not None and lin2_rmse is not None:
        lines.append("## Comparação de modelos")
        lines.append(f"- Linear v1 (lags+calendário): MAE={lin_mae:.2f} RMSE={lin_rmse:.2f}")
        lines.append(f"- Linear v2 (lags+calendário+fim_semana): MAE={lin2_mae:.2f} RMSE={lin2_rmse:.2f}")
        lines.append("")
        if model_cmp_fig:
            lines.append(f"- Erro por hora (v1 vs v2): `{os.path.basename(model_cmp_fig)}`")
            lines.append("")
        if hourly_cmp_top is not None and not hourly_cmp_top.empty:
            lines.append("Top horários por ganho (MAE_v1 − MAE_v2):")
            lines.append("| Hora | MAE v1 | MAE v2 | Ganho |")
            lines.append("|---:|---:|---:|---:|")
            for _, r in hourly_cmp_top.iterrows():
                lines.append(f"| {int(r['hora'])} | {float(r['mae_v1']):.2f} | {float(r['mae_v2']):.2f} | {float(r['improvement']):.2f} |")
            if hourly_cmp_csv:
                lines.append(f"Arquivo completo: `{os.path.basename(hourly_cmp_csv)}`")
            lines.append("")
        if hourly_cmp_worst is not None and not hourly_cmp_worst.empty:
            lines.append("Piores horários (ganho negativo ou menor):")
            lines.append("| Hora | MAE v1 | MAE v2 | Ganho |")
            lines.append("|---:|---:|---:|---:|")
            for _, r in hourly_cmp_worst.iterrows():
                lines.append(f"| {int(r['hora'])} | {float(r['mae_v1']):.2f} | {float(r['mae_v2']):.2f} | {float(r['improvement']):.2f} |")
            lines.append("")
        if improvement_fig:
            lines.append(f"Ganho por hora (figura): `{os.path.basename(improvement_fig)}`")
            lines.append("")
    if cv_exp or cv_roll:
        lines.append("## Validação temporal")
        if cv_exp:
            lines.append("Expanding window (MAE/RMSE por ano de teste):")
            for item in cv_exp:
                lines.append(f"- {item['test_year']}: MAE={item['mae']:.2f} RMSE={item['rmse']:.2f}")
        if cv_roll:
            lines.append("Rolling window (MAE/RMSE por ano de teste):")
            for item in cv_roll:
                lines.append(f"- {item['test_year']}: MAE={item['mae']:.2f} RMSE={item['rmse']:.2f}")
        lines.append("")
    if cv_exp2 or cv_roll2:
        lines.append("Validação temporal (modelo v2)")
        if cv_exp2:
            lines.append("Expanding window (MAE/RMSE por ano de teste):")
            for item in cv_exp2:
                lines.append(f"- {item['test_year']}: MAE={item['mae']:.2f} RMSE={item['rmse']:.2f}")
        if cv_roll2:
            lines.append("Rolling window (MAE/RMSE por ano de teste):")
            for item in cv_roll2:
                lines.append(f"- {item['test_year']}: MAE={item['mae']:.2f} RMSE={item['rmse']:.2f}")
        lines.append("")
    if resid_hist or resid_hour:
        lines.append("## Diagnóstico de resíduos")
        if resid_hist:
            lines.append(f"- Histograma de resíduos: `{os.path.basename(resid_hist)}`")
        if resid_hour:
            lines.append(f"- Erro por hora do dia: `{os.path.basename(resid_hour)}`")
        lines.append("")
    if resid_hist2 or resid_hour2:
        lines.append("Diagnóstico de resíduos (modelo v2)")
        if resid_hist2:
            lines.append(f"- Histograma de resíduos: `{os.path.basename(resid_hist2)}`")
        if resid_hour2:
            lines.append(f"- Erro por hora do dia: `{os.path.basename(resid_hour2)}`")
        # Figura adicional opcional: comparação feriado vs não feriado
        holi_cmp = os.path.join(os.path.dirname(resid_hour2), 'mvp_resid_hour_holiday_AEP_v2.png')
        lines.append(f"- Erro por hora (feriado vs não feriado): `{os.path.basename(holi_cmp)}`")
        lines.append("")
    lines.append("## Conexão com elasticidade e smart energy")
    lines.append("Identificar janelas de pico e vale próximas como candidatos a deslocamento. Próximo passo: conectar variação de carga à elasticidade do processo para simular suavização.")
    with open(path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))


def main():
    """
    Pipeline principal:
    1) Carrega AEP e PJM_Load
    2) Adiciona features temporais
    3) Gera EDA operacional (histogramas, curvas hora/dia)
    4) Calcula fator de carga diário e pico vs média
    5) Treina baseline e regressão linear; calcula métricas
    6) Escreve relatório MVP e imprime caminho
    """
    base = os.environ.get('DATA_ROOT', os.getcwd())
    out = os.path.join(base, 'reports', 'figures')
    ensure_dir(out)
    show = (os.environ.get('SHOW_PLOTS', '0') == '1') or ('COLAB_RELEASE_TAG' in os.environ)
    aep_col = 'AEP_MW'
    pjm_col = 'PJM_Load_MW'
    aep = load_series(os.path.join(base, 'data', 'raw', 'AEP_hourly.csv'), aep_col)
    pjm = load_series(os.path.join(base, 'data', 'raw', 'PJM_Load_hourly.csv'), pjm_col)
    aep = add_time_features(aep)
    pjm = add_time_features(pjm)
    aep_hist = os.path.join(out, 'mvp_hist_AEP.png')
    pjm_hist = os.path.join(out, 'mvp_hist_PJM_Load.png')
    plot_histogram(aep, aep_col, aep_hist, show=show)
    plot_histogram(pjm, pjm_col, pjm_hist, show=show)
    last_year = int(aep['ano'].max())
    aep_hour_curve = os.path.join(out, f'mvp_hourcurve_AEP_{last_year}.png')
    pjm_hour_curve = os.path.join(out, f'mvp_hourcurve_PJM_Load_{last_year}.png')
    hourly_curve_year(aep, aep_col, last_year, aep_hour_curve, show=show)
    hourly_curve_year(pjm, pjm_col, last_year, pjm_hour_curve, show=show)
    aep_dow_curve = os.path.join(out, 'mvp_dowcurve_AEP.png')
    pjm_dow_curve = os.path.join(out, 'mvp_dowcurve_PJM_Load.png')
    dow_curve(aep, aep_col, aep_dow_curve, show=show)
    dow_curve(pjm, pjm_col, pjm_dow_curve, show=show)
    v_top, i_top = seasonal_hourly_diff(aep, aep_col)
    lf = daily_load_factor(aep, aep_col)
    lf_csv = os.path.join(base, 'reports', 'mvp_daily_load_factor_AEP.csv')
    lf.to_csv(lf_csv, index=False)
    lf_worst = lf.nsmallest(10, 'fator')
    peak_mean_plot = os.path.join(out, 'mvp_peak_vs_mean_AEP.png')
    plot_peak_vs_mean(lf, peak_mean_plot, show=show)
    df_time, X, y = build_features(aep, aep_col)
    ly, X_train, y_train, X_test, y_test = split_train_test(df_time, X, y)
    aep_subset = aep[aep['ano'] == ly][['Datetime', aep_col]]
    base_mae, base_rmse = baseline_prev(aep_subset, aep_col)
    beta = fit_linear_regression(X_train, y_train)
    y_pred = predict_linear_regression(X_test, beta)
    lin_mae, lin_rmse = metrics(y_test, y_pred)
    cv_exp = time_series_cv(df_time, X, y, n_splits=3, mode='expanding')
    cv_roll = time_series_cv(df_time, X, y, n_splits=3, mode='rolling')
    resid_hist = os.path.join(out, 'mvp_resid_hist_AEP.png')
    resid_hour = os.path.join(out, 'mvp_resid_hour_AEP.png')
    test_mask = (df_time['Datetime'].dt.year == ly).values
    df_time_test = df_time[test_mask]
    plot_residuals(y_test, y_pred, df_time_test, resid_hist, resid_hour, show=show)
    df_time2, X2, y2 = build_features_weekend(aep, aep_col)
    ly2, X_train2, y_train2, X_test2, y_test2 = split_train_test(df_time2, X2, y2)
    beta2 = fit_linear_regression(X_train2, y_train2)
    y_pred2 = predict_linear_regression(X_test2, beta2)
    lin2_mae, lin2_rmse = metrics(y_test2, y_pred2)
    cv_exp2 = time_series_cv(df_time2, X2, y2, n_splits=3, mode='expanding')
    cv_roll2 = time_series_cv(df_time2, X2, y2, n_splits=3, mode='rolling')
    resid_hist2 = os.path.join(out, 'mvp_resid_hist_AEP_v2.png')
    resid_hour2 = os.path.join(out, 'mvp_resid_hour_AEP_v2.png')
    test_mask2 = (df_time2['Datetime'].dt.year == ly2).values
    df_time_test2 = df_time2[test_mask2]
    plot_residuals(y_test2, y_pred2, df_time_test2, resid_hist2, resid_hour2, show=show)
    df_time_test2_flags = pd.merge(df_time_test2, aep[['Datetime','feriado']], on='Datetime', how='left')
    resid_holi_cmp = os.path.join(out, 'mvp_resid_hour_holiday_AEP_v2.png')
    plot_residuals_holiday_comparison(y_test2, y_pred2, df_time_test2_flags, resid_holi_cmp, show=show)
    resid_model_cmp = os.path.join(out, 'mvp_resid_hour_model_compare_AEP.png')
    plot_residuals_model_compare(y_test, y_pred, df_time_test, y_test2, y_pred2, df_time_test2, resid_model_cmp, show=show)
    hourly_top, hourly_full = hourly_error_table(y_test, y_pred, df_time_test, y_test2, y_pred2, df_time_test2)
    hourly_csv = os.path.join(base, 'reports', 'mvp_hourly_error_compare_AEP.csv')
    hourly_full.to_csv(hourly_csv, index=False)
    hourly_worst = hourly_full.sort_values('improvement', ascending=True).head(5)
    improvement_fig = os.path.join(out, 'mvp_hourly_improvement_AEP.png')
    plot_hourly_improvement_bar(hourly_full, improvement_fig, show=show)
    print("Baseline lag-1  -> MAE:", base_mae, "RMSE:", base_rmse)
    print("Linear v1       -> MAE:", lin_mae, "RMSE:", lin_rmse)
    print("Linear v2 (WE)  -> MAE:", lin2_mae, "RMSE:", lin2_rmse)
    print("CV expanding v1:", cv_exp)
    print("CV rolling  v1:", cv_roll)
    print("CV expanding v2:", cv_exp2)
    print("CV rolling  v2:", cv_roll2)
    report = os.path.join(base, 'reports', 'mvp_report.md')
    write_report(report, 'Suavização de curva de carga e identificação de picos/vales', aep_hist, pjm_hist, aep_hour_curve, pjm_hour_curve, aep_dow_curve, pjm_dow_curve, lf_csv, lf_worst, peak_mean_plot, base_mae, base_rmse, lin_mae, lin_rmse, ly, v_top, i_top, cv_exp=cv_exp, cv_roll=cv_roll, resid_hist=resid_hist, resid_hour=resid_hour, lin2_mae=lin2_mae, lin2_rmse=lin2_rmse, cv_exp2=cv_exp2, cv_roll2=cv_roll2, resid_hist2=resid_hist2, resid_hour2=resid_hour2, model_cmp_fig=resid_model_cmp, hourly_cmp_top=hourly_top, hourly_cmp_csv=hourly_csv, hourly_cmp_worst=hourly_worst, improvement_fig=improvement_fig)
    print(report)

if __name__ == '__main__':
    main()
