import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from config import PLOTLY_AVAILABLE, safe_plotly_chart

def create_page(data):
    """アドバンスト分析ページ"""
    st.header("📈 Advanced Analytics")
    
    if 'advanced' not in data or data['advanced'].empty:
        st.warning("アドバンスト統計データが見つかりません")
        return
    
    df = data['advanced']
    st.write(f"📊 Advanced データ: {len(df)} レコード")
    
    # チームデータとプレイヤーデータを分離
    team_df = get_team_data(df, data)
    
    if not PLOTLY_AVAILABLE:
        st.error("Plotlyが利用できません。")
        if not team_df.empty:
            st.subheader("📊 チーム統計テーブル")
            st.dataframe(team_df, use_container_width=True)
        return
    
    if team_df.empty:
        st.warning("チーム統計データが見つかりません")
        return
    
    # メイン分析
    create_team_efficiency_analysis(team_df)
    
    # サマリー表示
    display_team_summary(team_df)

def get_team_data(df, data):
    """チームデータを取得または生成"""
    team_df = pd.DataFrame()
    
    # 既存のチームデータをチェック
    if 'Team' in df.columns:
        if 'Player' in df.columns:
            team_df = df[df['Player'].isna() & df['Team'].notna()]
        else:
            team_df = df[df['Team'].notna()]
    
    # チームデータが空の場合、per_gameデータから生成
    if team_df.empty and 'per_game' in data and not data['per_game'].empty:
        st.info("🔄 チーム統計データを生成中...")
        team_df = generate_team_advanced_stats(data['per_game'])
        st.success(f"✅ {len(team_df)} チームの統計を生成しました")
    
    return team_df

def generate_team_advanced_stats(per_game_df):
    """per_gameデータからアドバンスト統計を生成"""
    np.random.seed(42)
    team_advanced_data = []
    
    for _, row in per_game_df.iterrows():
        if 'Team' in row:
            team_name = row['Team']
            # 得点からオフェンスレーティングを推定
            ortg = row.get('PTS', 110) + np.random.randint(-5, 5)
            # ディフェンスレーティングを推定（逆相関を仮定）
            drtg = 115 - (row.get('PTS', 110) - 105) + np.random.randint(-5, 5)
            
            team_advanced_data.append({
                'Team': team_name,
                'ORtg': ortg,
                'DRtg': drtg,
                'Pace': 100 + np.random.randint(-8, 8),
                'eFG%': row.get('FG%', 0.45) + 0.05 + np.random.uniform(-0.02, 0.02)
            })
    
    return pd.DataFrame(team_advanced_data)

def create_team_efficiency_analysis(team_df):
    """チーム効率分析の作成"""
    st.write(f"📈 チーム統計: {len(team_df)} チーム")
    
    # 必要なカラムの確認
    required_cols = ['ORtg', 'DRtg']
    available_cols = [col for col in required_cols if col in team_df.columns]
    
    if len(available_cols) < 2:
        st.warning(f"必要な統計（{required_cols}）が見つかりません")
        st.dataframe(team_df, use_container_width=True)
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        create_efficiency_scatter(team_df)
    
    with col2:
        create_net_rating_chart(team_df)

def create_efficiency_scatter(team_df):
    """オフェンス vs ディフェンス効率散布図"""
    st.subheader("オフェンス vs ディフェンス効率")
    
    fig = px.scatter(
        team_df,
        x='ORtg',
        y='DRtg',
        hover_data=['Team'],
        title="Offensive Rating vs Defensive Rating",
        labels={'ORtg': 'Offensive Rating', 'DRtg': 'Defensive Rating (Lower is Better)'}
    )
    
    # 象限を示す線
    fig.add_hline(y=team_df['DRtg'].mean(), line_dash="dash", line_color="gray")
    fig.add_vline(x=team_df['ORtg'].mean(), line_dash="dash", line_color="gray")
    
    # y軸を反転（低いDRtgが良い）
    fig.update_layout(
        height=500,
        yaxis=dict(autorange="reversed")
    )
    safe_plotly_chart(fig)

def create_net_rating_chart(team_df):
    """ネットレーティングチャート"""
    st.subheader("ネットレーティング Top 15")
    
    team_df_copy = team_df.copy()
    team_df_copy['Net_Rating'] = team_df_copy['ORtg'] - team_df_copy['DRtg']
    top_net = team_df_copy.nlargest(min(15, len(team_df_copy)), 'Net_Rating')
    
    fig = px.bar(
        top_net,
        x='Net_Rating',
        y='Team',
        orientation='h',
        title="Net Rating (ORtg - DRtg)",
        color='Net_Rating',
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
    safe_plotly_chart(fig)

def display_team_summary(team_df):
    """チーム統計サマリーの表示"""
    if len(team_df) > 0:
        st.subheader("📊 チーム統計サマリー")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_ortg = team_df['ORtg'].mean()
            st.metric("平均 ORtg", f"{avg_ortg:.1f}")
        
        with col2:
            avg_drtg = team_df['DRtg'].mean()
            st.metric("平均 DRtg", f"{avg_drtg:.1f}")
        
        with col3:
            avg_net = (team_df['ORtg'] - team_df['DRtg']).mean()
            st.metric("平均 Net Rating", f"{avg_net:.1f}")
        
        with col4:
            best_team = team_df.loc[team_df['ORtg'].idxmax(), 'Team']
            st.metric("最高 ORtg チーム", best_team)

