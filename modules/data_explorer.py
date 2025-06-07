import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from config import PLOTLY_AVAILABLE, safe_plotly_chart
from utils.helpers import filter_multi_team_records

def create_page(data):
    """データエクスプローラーページ"""
    st.header("🔍 Data Explorer")
    
    st.info("""
    **🔍 データエクスプローラーについて**
    
    豊富なNBAデータを自由に探索・分析できるツールです：
    - **データセット選択**: per_game, advanced, play_by_play等から選択
    - **インタラクティブフィルタ**: 数値範囲、カテゴリー、チーム等で絞り込み
    - **カスタム可視化**: X軸・Y軸を自由に設定してグラフ作成
    - **詳細検索**: 特定の条件を満たす選手やチームを発見
    """)
    st.divider()
    
    # 利用可能なデータセットを取得
    available_datasets = get_available_datasets(data)
    
    if not available_datasets:
        st.error("利用可能なデータセットがありません")
        return
    
    # データセット選択
    dataset_choice = st.selectbox(
        "探索するデータセットを選択:",
        options=available_datasets,
        format_func=lambda x: {
            'per_game': 'Per Game Stats',
            'advanced': 'Advanced Stats', 
            'play_by_play': 'Play-by-Play Stats',
            'team_salaries': 'Team Salaries',
            'player_salaries': 'Player Salaries'
        }.get(x, x)
    )
    
    if dataset_choice in data:
        explore_dataset(data[dataset_choice], dataset_choice)

def get_available_datasets(data):
    """利用可能なデータセットのリストを取得"""
    available_datasets = []
    for key, df in data.items():
        if not df.empty:
            available_datasets.append(key)
    return available_datasets

def explore_dataset(df, dataset_name):
    """データセットの探索"""
    df = filter_multi_team_records(df.copy())
    
    # データセット概要
    display_dataset_overview(df, dataset_name)
    
    # フィルタリング機能
    df_filtered = apply_data_filters(df)
    
    # データ表示
    display_data_table(df_filtered)
    
    # 統計サマリー
    display_statistical_summary(df_filtered)
    
    # 簡単な可視化
    if PLOTLY_AVAILABLE:
        create_simple_visualizations(df_filtered)

def display_dataset_overview(df, dataset_name):
    """データセット概要の表示"""
    st.subheader(f"📊 {dataset_name} データセット概要")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("レコード数", len(df))
    
    with col2:
        st.metric("カラム数", len(df.columns))
    
    with col3:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        st.metric("数値カラム数", len(numeric_cols))
    
    with col4:
        null_count = df.isnull().sum().sum()
        st.metric("欠損値数", null_count)

def apply_data_filters(df):
    """データフィルタリングの適用"""
    st.subheader("🔍 フィルター")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 数値フィルター
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            filter_col = st.selectbox("フィルターする列:", options=['なし'] + numeric_cols)
            
            if filter_col != 'なし':
                min_val = float(df[filter_col].min())
                max_val = float(df[filter_col].max())
                
                if min_val < max_val:
                    range_values = st.slider(
                        f"{filter_col} の範囲:",
                        min_value=min_val,
                        max_value=max_val,
                        value=(min_val, max_val)
                    )
                    
                    df = df[(df[filter_col] >= range_values[0]) & (df[filter_col] <= range_values[1])]
    
    with col2:
        # ソート機能
        if numeric_cols:
            sort_col = st.selectbox("ソートする列:", options=['なし'] + numeric_cols)
            if sort_col != 'なし':
                sort_ascending = st.checkbox("昇順", value=False)
                df = df.sort_values(sort_col, ascending=sort_ascending)
    
    return df

def display_data_table(df):
    """データテーブルの表示"""
    st.subheader("📊 データテーブル")
    
    # 表示行数の選択
    max_rows = min(len(df), 1000)
    if max_rows > 0:
        display_rows = st.slider("表示行数:", min_value=10, max_value=max_rows, value=min(50, max_rows))
        st.dataframe(df.head(display_rows), use_container_width=True)
    else:
        st.warning("表示するデータがありません")

def display_statistical_summary(df):
    """統計サマリーの表示"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if numeric_cols:
        st.subheader("📈 統計サマリー")
        summary_stats = df[numeric_cols].describe()
        st.dataframe(summary_stats, use_container_width=True)

def create_simple_visualizations(df):
    """簡単な可視化の作成"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) >= 2:
        st.subheader("📊 簡単な可視化")
        
        col1, col2 = st.columns(2)
        
        with col1:
            x_axis = st.selectbox("X軸:", options=numeric_cols)
        
        with col2:
            y_axis = st.selectbox("Y軸:", options=numeric_cols, index=1 if len(numeric_cols) > 1 else 0)
        
        if x_axis != y_axis:
            create_scatter_plot(df, x_axis, y_axis)

def create_scatter_plot(df, x_axis, y_axis):
    """散布図の作成"""
    fig = px.scatter(
        df, 
        x=x_axis, 
        y=y_axis, 
        title=f"{x_axis} vs {y_axis}",
        hover_data=[col for col in ['Team', 'Player', 'Tm'] if col in df.columns]
    )
    fig.update_layout(height=500)
    safe_plotly_chart(fig)

