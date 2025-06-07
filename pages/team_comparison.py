import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from config import PLOTLY_AVAILABLE, safe_plotly_chart

def create_page(data):
    """チーム比較ページ"""
    st.header("⚖️ Team Comparison")
    
    if 'per_game' not in data or data['per_game'].empty:
        st.error("Per game データが見つかりません")
        return
    
    df = data['per_game']
    
    if 'Team' not in df.columns:
        st.error("チーム情報が見つかりません")
        return
    
    # チーム選択
    teams = st.multiselect(
        "比較するチームを選択してください（最大6チーム）:",
        options=df['Team'].tolist(),
        default=df['Team'].tolist()[:4],
        max_selections=6
    )
    
    if not teams:
        st.warning("チームを選択してください")
        return
    
    selected_df = df[df['Team'].isin(teams)]
    
    # 比較統計の選択
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    stats_options = [col for col in numeric_cols if col in ['PTS', 'FG%', '3P%', 'REB', 'AST', 'STL', 'BLK', 'TOV']]
    
    selected_stats = st.multiselect(
        "比較する統計を選択:",
        options=stats_options,
        default=stats_options[:4] if len(stats_options) >= 4 else stats_options
    )
    
    if not selected_stats:
        st.warning("比較する統計を選択してください")
        return
    
    if PLOTLY_AVAILABLE:
        # レーダーチャート
        st.subheader("レーダーチャート比較")
        create_radar_chart(df, selected_df, teams, selected_stats)
        
        # 棒グラフ比較
        st.subheader("統計比較（棒グラフ）")
        create_comparison_bar_chart(selected_df, selected_stats)
    
    # 比較テーブル
    st.subheader("📊 詳細比較テーブル")
    comparison_table = selected_df[['Team'] + selected_stats].copy()
    st.dataframe(comparison_table, use_container_width=True)

def create_radar_chart(df, selected_df, teams, selected_stats):
    """レーダーチャートの作成"""
    fig = go.Figure()
    
    for team in teams:
        team_data = selected_df[selected_df['Team'] == team]
        if not team_data.empty:
            values = []
            for stat in selected_stats:
                # 正規化（0-1スケール）
                min_val = df[stat].min()
                max_val = df[stat].max()
                normalized = (team_data[stat].iloc[0] - min_val) / (max_val - min_val) if max_val > min_val else 0
                values.append(normalized)
            
            values += values[:1]  # 円を閉じる
            stats_labels = selected_stats + [selected_stats[0]]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=stats_labels,
                fill='toself',
                name=team
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        height=500
    )
    
    safe_plotly_chart(fig)

def create_comparison_bar_chart(selected_df, selected_stats):
    """比較棒グラフの作成"""
    comparison_df = selected_df[['Team'] + selected_stats].melt(
        id_vars=['Team'], 
        var_name='Statistic', 
        value_name='Value'
    )
    
    fig = px.bar(
        comparison_df,
        x='Team',
        y='Value',
        color='Statistic',
        barmode='group',
        title="選択チームの統計比較"
    )
    fig.update_layout(height=400)
    safe
