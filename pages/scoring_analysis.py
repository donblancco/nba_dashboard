import streamlit as st
import plotly.express as px
from config import PLOTLY_AVAILABLE, safe_plotly_chart, check_required_columns

def create_page(data):
    """得点分析ページ"""
    st.header("📊 Scoring Analysis")
    
    if 'per_game' not in data or data['per_game'].empty:
        st.error("Per game データが見つかりません")
        return
    
    df = data['per_game']
    
    if not PLOTLY_AVAILABLE:
        st.error("Plotlyが利用できません。")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        if check_required_columns(df, ['Team', 'PTS'], "得点データ"):
            st.subheader("得点ランキング Top 15")
            top_scoring = df.nlargest(15, 'PTS')
            
            fig = px.bar(
                top_scoring, 
                x='PTS', 
                y='Team',
                orientation='h',
                title="1試合平均得点",
                color='PTS',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
            safe_plotly_chart(fig)
    
    with col2:
        if check_required_columns(df, ['FG%', '3P%', 'Team'], "シュート効率データ"):
            st.subheader("シュート効率分析")
            
            fig = px.scatter(
                df,
                x='FG%',
                y='3P%',
                hover_data=['Team'],
                title="FG% vs 3P%",
                labels={'FG%': 'Field Goal %', '3P%': '3-Point %'}
            )
            
            fig.add_hline(y=df['3P%'].mean(), line_dash="dash", line_color="red", 
                         annotation_text=f"平均3P%: {df['3P%'].mean():.3f}")
            fig.add_vline(x=df['FG%'].mean(), line_dash="dash", line_color="red",
                         annotation_text=f"平均FG%: {df['FG%'].mean():.3f}")
            
            fig.update_layout(height=500)
            safe_plotly_chart(fig)

