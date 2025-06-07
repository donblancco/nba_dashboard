import streamlit as st
import plotly.express as px
from config import PLOTLY_AVAILABLE, safe_plotly_chart, check_required_columns
from utils.helpers import filter_multi_team_records

def create_page(data):
    """得点分析ページ"""
    st.header("📊 Scoring Analysis")
    
    if 'per_game' not in data or data['per_game'].empty:
        st.error("Per game データが見つかりません")
        return
    
    df = filter_multi_team_records(data['per_game'])
    
    if not PLOTLY_AVAILABLE:
        st.error("Plotlyが利用できません。")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        if check_required_columns(df, ['Player', 'Team', 'PTS'], "得点データ"):
            st.subheader("得点ランキング Top 15")
            
            # 同じ選手の重複を除去し、最新チーム（TOTを優先、なければ最後のレコード）を使用
            df_unique = df.copy()
            
            # 各選手について、TOTチームがあれば優先、なければ最後のレコードを使用
            def get_latest_team_record(group):
                tot_records = group[group['Team'] == 'TOT']
                if not tot_records.empty:
                    return tot_records.iloc[-1]
                else:
                    return group.iloc[-1]
            
            df_unique = df_unique.groupby('Player').apply(get_latest_team_record).reset_index(drop=True)
            
            top_scoring = df_unique.nlargest(15, 'PTS')[['Player', 'Team', 'PTS']]
            
            # プレイヤー名とチーム名を組み合わせて表示
            top_scoring['player_display'] = top_scoring['Player'] + ' (' + top_scoring['Team'] + ')'
            
            fig = px.bar(
                top_scoring, 
                x='PTS', 
                y='player_display',
                orientation='h',
                title="1試合平均得点ランキング (選手別)",
                color='PTS',
                color_continuous_scale='Viridis',
                text='PTS'
            )
            fig.update_layout(
                height=600, 
                yaxis={'categoryorder':'total ascending'},
                xaxis_title="平均得点",
                yaxis_title="選手 (チーム)",
                title_x=0.5
            )
            fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
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

