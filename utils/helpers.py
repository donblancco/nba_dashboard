import pandas as pd
import numpy as np

def clean_player_names(names):
    """プレイヤー名のクリーニング"""
    if isinstance(names, pd.Series):
        return names.str.strip().str.title()
    elif isinstance(names, list):
        return [name.strip().title() if isinstance(name, str) else name for name in names]
    else:
        return str(names).strip().title()

def calculate_efficiency_metrics(df, stat_col, salary_col):
    """効率メトリクスの計算"""
    df = df.copy()
    
    # 数値変換
    stat_values = pd.to_numeric(df[stat_col], errors='coerce').fillna(0)
    salary_values = pd.to_numeric(df[salary_col], errors='coerce').fillna(1)
    
    # ゼロ除算を防ぐ
    salary_values = salary_values.replace(0, 1)
    
    # 効率計算
    efficiency = (stat_values / salary_values) * 1000000
    
    return efficiency

def format_large_numbers(number):
    """大きな数値のフォーマット"""
    if number >= 1000000:
        return f"{number/1000000:.1f}M"
    elif number >= 1000:
        return f"{number/1000:.1f}K"
    else:
        return f"{number:.0f}"

def get_percentile_rank(series, value):
    """パーセンタイル順位の計算"""
    return (series < value).mean() * 100

def filter_multi_team_records(df, team_columns=['Team', 'Tm']):
    """2TM、3TM等の複数チーム移籍レコードを除外"""
    df_filtered = df.copy()
    
    for col in team_columns:
        if col in df_filtered.columns:
            # 2TM, 3TM, 4TM等のパターンを除外
            df_filtered = df_filtered[~df_filtered[col].astype(str).str.match(r'^\d+TM$', na=False)]
    
    return df_filtered
