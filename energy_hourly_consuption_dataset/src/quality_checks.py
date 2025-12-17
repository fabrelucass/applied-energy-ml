import os
import hashlib
import json
import pandas as pd

def md5_file(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def list_raw_files(root):
    raw = os.path.join(root, 'data', 'raw')
    files = []
    for name in os.listdir(raw):
        if name.lower().endswith('.csv'):
            files.append(os.path.join(raw, name))
    return files

def basic_checks(path):
    df = pd.read_csv(path, nrows=5000)
    cols = list(df.columns)
    ok_datetime = 'Datetime' in cols
    n_rows = len(df)
    dups = int(df.duplicated(subset=['Datetime']).sum()) if ok_datetime else None
    miss = {c: int(df[c].isna().sum()) for c in cols}
    return {
        'columns': cols,
        'has_datetime': ok_datetime,
        'sample_rows': n_rows,
        'duplicated_by_datetime': dups,
        'missing_counts': miss,
    }

def write_manifest(root, files):
    items = []
    for p in files:
        items.append({
            'file': os.path.relpath(p, root),
            'size': os.path.getsize(p),
            'md5': md5_file(p),
        })
    man = {
        'root': root,
        'files': items,
    }
    out = os.path.join(root, 'data', 'manifest.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(man, f, indent=2)
    return out

def write_quality_report(root, checks):
    lines = []
    lines.append('# Relatório de Qualidade dos Dados (Raw)')
    lines.append('')
    for item in checks:
        lines.append(f"Arquivo: `{os.path.basename(item['file'])}`")
        lines.append(f"- Colunas: {', '.join(item['info']['columns'])}")
        lines.append(f"- Possui Datetime: {item['info']['has_datetime']}")
        lines.append(f"- Linhas amostradas: {item['info']['sample_rows']}")
        if item['info']['duplicated_by_datetime'] is not None:
            lines.append(f"- Duplicatas por Datetime: {item['info']['duplicated_by_datetime']}")
        lines.append("- Ausentes (amostra):")
        for c, v in item['info']['missing_counts'].items():
            lines.append(f"  - {c}: {v}")
        lines.append('')
    out = os.path.join(root, 'reports', 'quality_report.md')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return out

def main():
    root = os.getcwd()
    files = list_raw_files(root)
    checks = []
    for p in files:
        info = basic_checks(p)
        checks.append({'file': p, 'info': info})
    man = write_manifest(root, files)
    rep = write_quality_report(root, checks)
    print(man)
    print(rep)

if __name__ == '__main__':
    main()

