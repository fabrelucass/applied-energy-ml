import sys
import os
import math
import itertools
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def _detect_datetime_columns(df):
    dt_cols = []
    for col in df.columns:
        name = str(col).lower()
        if name in ("datetime", "date", "timestamp"):
            dt_cols.append(col)
    return dt_cols

def _classify_columns(df):
    types = {}
    dt_cols = _detect_datetime_columns(df)
    for c in df.columns:
        if c in dt_cols:
            types[c] = 'data'
            continue
        if pd.api.types.is_numeric_dtype(df[c]):
            types[c] = 'numerico'
        elif pd.api.types.is_bool_dtype(df[c]):
            types[c] = 'categorico'
        else:
            s = df[c].astype(str)
            lens = s.str.len()
            uniq = df[c].nunique(dropna=True)
            ratio = uniq / max(len(df), 1)
            avg_len = lens.mean()
            if ratio < 0.3 and avg_len < 30:
                types[c] = 'categorico'
            else:
                types[c] = 'texto'
    return types, dt_cols

def _convert_datetimes(df, dt_cols):
    for c in dt_cols:
        df[c] = pd.to_datetime(df[c], errors='coerce')
    return df

def _basic_info(df, types):
    cols = list(df.columns)
    n_rows = len(df)
    n_cols = len(cols)
    dtypes = {c: types[c] for c in cols}
    return cols, n_rows, n_cols, dtypes

def _missing_values(df):
    res = []
    for c in df.columns:
        miss = df[c].isna().sum()
        res.append((c, int(miss), float(miss/len(df) if len(df) else 0)))
    return res

def _numeric_stats(df, types):
    num_cols = [c for c,t in types.items() if t == 'numerico']
    stats = {}
    for c in num_cols:
        s = pd.to_numeric(df[c], errors='coerce')
        stats[c] = {
            'count': int(s.count()),
            'mean': float(s.mean()) if s.count() else np.nan,
            'median': float(s.median()) if s.count() else np.nan,
            'std': float(s.std()) if s.count() else np.nan,
            'min': float(s.min()) if s.count() else np.nan,
            'max': float(s.max()) if s.count() else np.nan,
            'skew': float(s.skew()) if s.count() else np.nan
        }
    return stats, num_cols

def _categorical_cardinality(df, types):
    cat_cols = [c for c,t in types.items() if t == 'categorico']
    card = {}
    for c in cat_cols:
        card[c] = int(df[c].nunique(dropna=True))
    return card, cat_cols

def _detect_outliers_iqr(df, num_cols):
    outliers = {}
    for c in num_cols:
        s = pd.to_numeric(df[c], errors='coerce').dropna()
        if s.empty:
            outliers[c] = {'count': 0, 'ratio': 0.0}
            continue
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = (s < lower) | (s > upper)
        cnt = int(mask.sum())
        outliers[c] = {'count': cnt, 'ratio': float(cnt/len(s))}
    return outliers

def _duplicate_analysis(df):
    total = len(df)
    full_dups = int(df.duplicated().sum())
    full_ratio = float(full_dups/total) if total else 0.0
    uniq_ratio = {}
    for c in df.columns:
        uniq_ratio[c] = float(df[c].nunique(dropna=True)/total) if total else 0.0
    candidates = [c for c,r in sorted(uniq_ratio.items(), key=lambda x: -x[1]) if r >= 0.7]
    combos = []
    for k in [2,3]:
        for combo in itertools.combinations(candidates, k):
            combos.append(combo)
    partial = []
    for combo in combos[:20]:
        d = int(df.duplicated(subset=list(combo)).sum())
        r = float(d/total) if total else 0.0
        partial.append({'columns': list(combo), 'count': d, 'ratio': r})
    return {'full_count': full_dups, 'full_ratio': full_ratio, 'partial': partial}

def _ensure_dir(d):
    os.makedirs(d, exist_ok=True)

def _plot_numeric_histograms(df, num_cols, out_dir):
    imgs = []
    cols = num_cols[:10]
    for c in cols:
        s = pd.to_numeric(df[c], errors='coerce')
        plt.figure(figsize=(8,5))
        sns.histplot(s, bins=30, kde=True)
        plt.title(f"Histograma: {c}")
        plt.xlabel(c)
        plt.tight_layout()
        fn = os.path.join(out_dir, f"eda_hist_{c}.png")
        plt.savefig(fn)
        plt.close()
        imgs.append(fn)
    return imgs

def _plot_categorical_bars(df, cat_cols, out_dir):
    imgs = []
    cols = cat_cols[:10]
    for c in cols:
        vc = df[c].value_counts(dropna=False).head(20)
        plt.figure(figsize=(10,6))
        sns.barplot(x=vc.values, y=vc.index, orient='h')
        plt.title(f"Top categorias: {c}")
        plt.xlabel("Frequência")
        plt.ylabel(c)
        plt.tight_layout()
        fn = os.path.join(out_dir, f"eda_bar_{c}.png")
        plt.savefig(fn)
        plt.close()
        imgs.append(fn)
    return imgs

def _plot_corr_heatmap(df, num_cols, out_dir):
    if len(num_cols) < 2:
        return None
    corr = df[num_cols].apply(pd.to_numeric, errors='coerce').corr(method='pearson')
    plt.figure(figsize=(max(8, len(num_cols)), max(6, len(num_cols))))
    sns.heatmap(corr, annot=False, cmap='viridis')
    plt.title("Matriz de correlação (Pearson)")
    plt.tight_layout()
    fn = os.path.join(out_dir, "eda_corr_heatmap.png")
    plt.savefig(fn)
    plt.close()
    return fn

def _format_pct(x):
    return f"{x*100:.2f}%"

def _acronym_info():
    return {
        'AEP': ('American Electric Power', 'Vários estados na zona AEP (PJM)'),
        'COMED': ('Commonwealth Edison Company', 'Norte de Illinois (Chicago)'),
        'DAYTON': ('Dayton Power & Light', 'Região de Dayton, Ohio'),
        'DEOK': ('Duke Energy Ohio & Kentucky', 'Zona Ohio/Kentucky'),
        'DOM': ('Dominion Energy', 'Principalmente Virgínia e arredores'),
        'DUQ': ('Duquesne Light', 'Região de Pittsburgh, PA'),
        'EKPC': ('East Kentucky Power Cooperative', 'Leste de Kentucky'),
        'FE': ('FirstEnergy (ATSI e afins)', 'Utilities em OH, PA e região'),
        'NI': ('Northern Indiana Public Service (NIPSCO)', 'Norte de Indiana'),
        'PJM_Load': ('Carga total PJM', 'Sistema agregado da PJM')
    }

def _example_problematic_rows(df):
    examples_missing = []
    examples_outliers = []
    if 'PJM_Load' in df.columns:
        miss_rows = df[df['PJM_Load'].isna()].head(3)
        for _, row in miss_rows.iterrows():
            examples_missing.append(f"Datetime={row.get('Datetime')}, PJM_Load={row.get('PJM_Load')}")
    if 'FE' in df.columns:
        s = pd.to_numeric(df['FE'], errors='coerce')
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = (s < lower) | (s > upper)
        out_rows = df[mask].head(3)
        for _, row in out_rows.iterrows():
            examples_outliers.append(f"Datetime={row.get('Datetime')}, FE={row.get('FE')}")
    return examples_missing, examples_outliers

def _write_report(md_path, file_path, cols, n_rows, n_cols, dtypes, missing, stats, card, dup, num_imgs, cat_imgs, corr_img, outliers, context_name, acronyms, examples_missing, examples_outliers):
    lines = []
    lines.append(f"# Relatório de Análise Exploratória")
    lines.append("")
    lines.append(f"Arquivo analisado: `{os.path.basename(file_path)}`")
    lines.append(f"Conteúdo: {context_name}")
    lines.append("")
    lines.append("## 1. Estrutura dos dados")
    lines.append(f"Total de registros: {n_rows}")
    lines.append(f"Total de colunas: {n_cols}")
    lines.append("Colunas e tipos:")
    for c in cols:
        lines.append(f"- {c}: {dtypes[c]}")
    lines.append("")
    lines.append("## 1.1 Significados das siglas")
    lines.append("Tabela rápida:")
    for sigla, (significado, regiao) in acronyms.items():
        if sigla in cols:
            lines.append(f"- {sigla}: {significado} — {regiao}")
    lines.append("")
    lines.append("## 2. Qualidade dos dados")
    lines.append("Valores ausentes por coluna:")
    for c, cnt, pct in missing:
        lines.append(f"- {c}: {cnt} ({_format_pct(pct)})")
    lines.append("")
    lines.append("Estatísticas básicas (numéricas):")
    for c, st in stats.items():
        lines.append(f"- {c}: média {st['mean']}, mediana {st['median']}, desvio {st['std']}, min {st['min']}, max {st['max']}, skew {st['skew']}")
    lines.append("")
    lines.append("Outliers (IQR):")
    for c, oi in outliers.items():
        lines.append(f"- {c}: {oi['count']} ({_format_pct(oi['ratio'])})")
    lines.append("")
    lines.append("Cardinalidade (categóricas):")
    for c, k in card.items():
        lines.append(f"- {c}: {k} categorias")
    lines.append("")
    lines.append("## 3. Duplicatas")
    lines.append(f"Registros duplicados completos: {dup['full_count']} ({_format_pct(dup['full_ratio'])})")
    if dup['partial']:
        lines.append("Duplicatas parciais (combinações potenciais):")
        for item in dup['partial']:
            lines.append(f"- {', '.join(item['columns'])}: {item['count']} ({_format_pct(item['ratio'])})")
    lines.append("")
    lines.append("## 3.1 Exemplos de dados problemáticos")
    if examples_missing:
        lines.append("Valores ausentes (amostras):")
        for e in examples_missing:
            lines.append(f"- {e}")
    if examples_outliers:
        lines.append("Outliers (amostras):")
        for e in examples_outliers:
            lines.append(f"- {e}")
    lines.append("")
    lines.append("## 4. Visualizações")
    if num_imgs:
        lines.append("Histogramas (numéricos):")
        for p in num_imgs:
            lines.append(f"- `{os.path.basename(p)}`")
    if cat_imgs:
        lines.append("Gráficos de barras (categóricas):")
        for p in cat_imgs:
            lines.append(f"- `{os.path.basename(p)}`")
    if corr_img:
        lines.append(f"Matriz de correlação: `{os.path.basename(corr_img)}`")
    lines.append("")
    lines.append("## 5. Problemas e recomendações")
    issues = []
    for c, cnt, pct in missing:
        if pct > 0.05:
            issues.append(f"Valores ausentes elevados em {c}")
    for c, st in stats.items():
        if not math.isnan(st['std']) and st['std'] == 0:
            issues.append(f"Variância nula em {c}")
    if dup['full_ratio'] > 0:
        issues.append("Duplicatas completas presentes")
    lines.append("Problemas identificados:")
    if issues:
        for i in issues:
            lines.append(f"- {i}")
    else:
        lines.append("- Nenhum problema relevante identificado")
    lines.append("")
    lines.append("Recomendações:")
    if issues:
        lines.append("- Remover/agrupá duplicatas conforme regras de negócio (chave: Datetime)")
        lines.append("- Tratar ausentes com interpolação temporal ou mediana sazonal por hora/mês")
        lines.append("- Tratar outliers via winsorização (IQR) ou cap em percentis 1º/99º")
        lines.append("- Validar consistência temporal e períodos de feriados/fins de semana")
    else:
        lines.append("- Prosseguir com modelagem ou análises avançadas")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

def generate_eda_report(file_path, output_dir):
    _ensure_dir(output_dir)
    df = pd.read_csv(file_path, low_memory=False)
    types, dt_cols = _classify_columns(df)
    df = _convert_datetimes(df, dt_cols)
    cols, n_rows, n_cols, dtypes = _basic_info(df, types)
    missing = _missing_values(df)
    stats, num_cols = _numeric_stats(df, types)
    card, cat_cols = _categorical_cardinality(df, types)
    outliers = _detect_outliers_iqr(df, num_cols)
    dup = _duplicate_analysis(df)
    examples_missing, examples_outliers = _example_problematic_rows(df)
    num_imgs = _plot_numeric_histograms(df, num_cols, output_dir)
    cat_imgs = _plot_categorical_bars(df, cat_cols, output_dir)
    corr_img = _plot_corr_heatmap(df, num_cols, output_dir)
    md_path = os.path.join(os.path.dirname(output_dir), 'eda_report.md')
    _write_report(
        md_path,
        file_path,
        cols,
        n_rows,
        n_cols,
        dtypes,
        missing,
        stats,
        card,
        dup,
        num_imgs,
        cat_imgs,
        corr_img,
        outliers,
        context_name="Hourly Energy Consumption",
        acronyms=_acronym_info(),
        examples_missing=examples_missing,
        examples_outliers=examples_outliers,
    )
    return {
        'report_path': md_path,
        'num_images': num_imgs,
        'cat_images': cat_imgs,
        'corr_image': corr_img,
        'outliers': outliers
    }

def main():
    base = os.getcwd()
    default_file = os.path.join(base, 'data', 'raw', 'PJM_Load_hourly.csv')
    file_path = sys.argv[1] if len(sys.argv) > 1 else default_file
    out_dir = os.path.join(base, 'reports', 'figures')
    res = generate_eda_report(file_path, out_dir)
    print(res['report_path'])

if __name__ == '__main__':
    main()

