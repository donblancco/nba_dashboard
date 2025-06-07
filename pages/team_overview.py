import streamlit as st
import pandas as pd
from config import check_required_columns

def create_page(data):
    """チーム概要ページ"""
    st.header("🏀 Team Overview")
    
    if 'per_game' not in data or data['per_game'].empty:
        st.error("Per game データが見つかりません")
        return
    
    df = data['per_game']
    
    # 必要なカラムのチェック
    required_cols = ['PTS', 'FG%', 'AST', 'REB']
    if not check_required_columns(df, required_cols, "チーム統計"):
        return
    
    # メトリクス表示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_pts = df['PTS'].mean()
        max_pts_team = df.loc[df['PTS'].idxmax(), 'Team'] if 'Team' in df.columns else "N/A"
        st.metric(
            label="平均得点",
            value=f"{avg_pts:.1f}",
            delta=f"最高: {max_pts_team}"
        )
    
    with col2:
        avg_fg = df['FG%'].mean()
        st.metric(
            label="平均FG%",
            value=f"{avg_fg:.3f}"
        )
    
    with col3:
        avg_ast = df['AST'].mean()
        st.metric(
            label="平均アシスト",
            value=f"{avg_ast:.1f}"
        )
    
    with col4:
        avg_reb = df['REB'].mean()
        st.metric(
            label="平均リバウンド",
            value=f"{avg_reb:.1f}"
        )
    
    # データテーブル
    st.subheader("📊 チームデータ")
    st.dataframe(df, use_container_width=True)

