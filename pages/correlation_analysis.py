import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from config import PLOTLY_AVAILABLE, safe_plotly_chart

def create_page(data):
    """相関分析ページ"""
    st.header("🔗 Correlation Analysis")
    
    if 'per_game' not in data or data['per_game'].empty:
        st.error("Per game データが見つかりません")
        return
    
    df = data['per_game']
    
    # 数値カラムのみ選択
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.error("相関分析に十分な数値データがありません")
        return
    
    # 統計選択
    selected_stats = st.multiselect(
        "相関分析する統計を選択:",
        options=numeric_cols,
        default=[col for col in numeric_cols if col in ['PTS', 'FG%', '3P%', 'REB', 'AST', 'STL', 'BLK']][:7]
    )
    
    if len(selected_stats) < 2:
        st.warning("2つ以上の統計を選択してください")
        return
    
    # 相関分析の実行
    perform_correlation_analysis(df, selected_stats)

def perform_correlation_analysis(df, selected_stats):
    """相関分析の実行"""
    correlation_matrix = df[selected_stats].corr()
    
    if PLOTLY_AVAILABLE:
        # ヒートマップ
        st.subheader("相関係数ヒートマップ")
        create_correlation_heatmap(correlation_matrix)
    
    # 強い相関の発見
    st.subheader("注目すべき相関関係")
    find_strong_correlations(correlation_matrix)
    
    # 相関行列の詳細テーブル
    st.subheader("📊 相関行列")
    display_correlation_matrix(correlation_matrix)

def create_correlation_heatmap(correlation_matrix):
    """相関ヒートマップの作成"""
    fig = px.imshow(
        correlation_matrix,
        text_auto=True,
        aspect="auto",
        title="統計間の相関係数",
        color_continuous_scale='RdBu_r',
        range_color=[-1, 1]
    )
    fig.update_layout(height=600)
    safe_plotly_chart(fig)

def find_strong_correlations(correlation_matrix):
    """強い相関関係の発見"""
    strong_correlations = []
    for i in range(len(correlation_matrix.columns)):
        for j in range(i+1, len(correlation_matrix.columns)):
            corr_value = correlation_matrix.iloc[i, j]
            if abs(corr_value) >= 0.7:
                strong_correlations.append({
                    'Stat 1': correlation_matrix.columns[i],
                    'Stat 2': correlation_matrix.columns[j],
                    'Correlation': round(corr_value, 4)
                })
    
    if strong_correlations:
        corr_df = pd.DataFrame(strong_correlations)
        corr_df = corr_df.sort_values('Correlation', key=abs, ascending=False)
        st.dataframe(corr_df, use_container_width=True)
    else:
        st.info("強い相関関係（|r| >= 0.7）は見つかりませんでした")

def display_correlation_matrix(correlation_matrix):
    """相関行列の表示"""
    st.dataframe(
        correlation_matrix.style.background_gradient(cmap='RdBu_r', vmin=-1, vmax=1).format("{:.4f}"),
        use_container_width=True
    )

