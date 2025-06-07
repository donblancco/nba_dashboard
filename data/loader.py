import streamlit as st
import pandas as pd
import os
from config import JSON_AVAILABLE
from .sample_data import create_sample_data

if JSON_AVAILABLE:
    import json

@st.cache_data
def load_nba_data(data_dir='nba_data'):
    """NBA データを読み込み（サイレントモード）"""
    data = {}
    
    if not os.path.exists(data_dir):
        # サイレントでサンプルデータを返す
        return create_sample_data()
    
    file_mappings = {
        'per_game': 'nba_2025_per_game_stats.json',
        'advanced': 'nba_2025_advanced_stats.json',
        'play_by_play': 'nba_2025_play_by_play_stats.json',
        'team_salaries': 'nba_team_salaries_2025.json',
        'player_salaries': 'nba_player_salaries_2025.json'
    }
    
    files_loaded = 0
    
    # サイレントでファイルを読み込み（UIメッセージなし）
    for key, filename in file_mappings.items():
        filepath = os.path.join(data_dir, filename)
        
        try:
            if os.path.exists(filepath):
                df = load_json_file(filepath)
                
                if not df.empty:
                    df = convert_numeric_columns(df)
                    data[key] = df
                    files_loaded += 1
                else:
                    data[key] = pd.DataFrame()
            else:
                data[key] = pd.DataFrame()
                
        except Exception:
            # エラーも表示せず、空のDataFrameを設定
            data[key] = pd.DataFrame()
    
    if files_loaded == 0:
        # サイレントでサンプルデータを返す
        return create_sample_data()
    
    # 何も表示せずに結果を返す
    return data

def load_json_file(filepath):
    """JSONファイルを読み込んでDataFrameに変換"""
    if not JSON_AVAILABLE:
        raise ImportError("JSONライブラリが利用できません")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            
        if isinstance(json_data, list):
            df = pd.DataFrame(json_data)
        elif isinstance(json_data, dict):
            # 辞書の場合、適切にDataFrameに変換
            if 'data' in json_data:
                df = pd.DataFrame(json_data['data'])
            else:
                df = pd.DataFrame([json_data])
        else:
            raise ValueError(f"サポートされていないJSON形式: {type(json_data)}")
        
        return df
        
    except json.JSONDecodeError as e:
        raise ValueError(f"JSONデコードエラー: {e}")
    except Exception as e:
        raise Exception(f"ファイル読み込みエラー: {e}")

def convert_numeric_columns(df):
    """数値カラムの変換"""
    # テキストカラムを除外
    text_columns = ['Team', 'Tm', 'player_name', 'team', 'source', 'Player', 'name']
    
    for col in df.columns:
        if col not in text_columns:
            df[col] = pd.to_numeric(df[col], errors='ignore')
    
    return df

def validate_data_structure(data):
    """データ構造の検証"""
    validation_results = {}
    
    # 必要なデータセットのチェック
    required_datasets = ['per_game', 'advanced']
    for dataset in required_datasets:
        if dataset in data and not data[dataset].empty:
            validation_results[dataset] = "✅ OK"
        else:
            validation_results[dataset] = "❌ Missing or Empty"
    
    # オプショナルなデータセットのチェック
    optional_datasets = ['player_salaries', 'team_salaries', 'play_by_play']
    for dataset in optional_datasets:
        if dataset in data and not data[dataset].empty:
            validation_results[dataset] = "✅ Available"
        else:
            validation_results[dataset] = "⚠️ Not Available"
    
    return validation_results

def get_data_summary(data):
    """データサマリーの取得"""
    summary = {}
    
    for key, df in data.items():
        if not df.empty:
            summary[key] = {
                'records': len(df),
                'columns': len(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'null_values': df.isnull().sum().sum()
            }
        else:
            summary[key] = {
                'records': 0,
                'columns': 0,
                'memory_usage': 0,
                'null_values': 0
            }
    
    return summary

def display_data_validation_report(data):
    """データ検証レポートの表示"""
    st.subheader("📋 データ検証レポート")
    
    validation_results = validate_data_structure(data)
    summary = get_data_summary(data)
    
    # 検証結果テーブル
    validation_df = pd.DataFrame([
        {
            'Dataset': dataset,
            'Status': status,
            'Records': summary.get(dataset, {}).get('records', 0),
            'Columns': summary.get(dataset, {}).get('columns', 0)
        }
        for dataset, status in validation_results.items()
    ])
    
    st.dataframe(validation_df, use_container_width=True)
    
    # メモリ使用量
    total_memory = sum(info.get('memory_usage', 0) for info in summary.values())
    st.info(f"💾 総メモリ使用量: {total_memory / 1024 / 1024:.2f} MB")
    
    return validation_results

@st.cache_data
def load_external_data_source(source_url):
    """外部データソースからの読み込み（将来の拡張用）"""
    # 将来的にAPIやWebからデータを取得する場合の準備
    st.info(f"🌐 外部データソース機能は開発中です: {source_url}")
    return create_sample_data()

def export_data_to_csv(data, output_dir='exported_data'):
    """データをCSVとしてエクスポート"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    exported_files = []
    
    for key, df in data.items():
        if not df.empty:
            filepath = os.path.join(output_dir, f"{key}.csv")
            df.to_csv(filepath, index=False)
            exported_files.append(filepath)
    
    return exported_files