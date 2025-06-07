import streamlit as st
from datetime import datetime
from config import setup_page_config
from data.loader import load_nba_data
from pages import (
    team_overview,
    scoring_analysis,
    team_comparison,
    advanced_analytics,
    salary_efficiency,
    correlation_analysis,
    data_explorer
)

def main():
    """メインアプリケーション"""
    # ページ設定
    setup_page_config()
    
    # タイトル
    st.title("🏀 NBA 2024-25 Analytics Dashboard")
    st.markdown("---")
    
    # データ読み込み（完全サイレント）
    data = load_nba_data()
    
    # サイドバーナビゲーション
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.selectbox(
        "分析ページを選択:",
        [
            "Team Overview",
            "Scoring Analysis", 
            "Team Comparison",
            "Advanced Analytics",
            "Salary Efficiency",
            "Correlation Analysis",
            "Data Explorer"
        ]
    )
    
    # データ情報表示
    display_data_info(data)
    
    # ページルーティング
    try:
        if page == "Team Overview":
            team_overview.create_page(data)
        elif page == "Scoring Analysis":
            scoring_analysis.create_page(data)
        elif page == "Team Comparison":
            team_comparison.create_page(data)
        elif page == "Advanced Analytics":
            advanced_analytics.create_page(data)
        elif page == "Salary Efficiency":
            salary_efficiency.create_page(data)
        elif page == "Correlation Analysis":
            correlation_analysis.create_page(data)
        elif page == "Data Explorer":
            data_explorer.create_page(data)
    except Exception as e:
        st.error(f"ページ表示エラー: {e}")
        st.write("エラー詳細:", str(e))
    
    # フッター
    st.markdown("---")
    st.markdown("### 🔄 Data Refresh")
    if st.button("データを再読み込み"):
        st.cache_data.clear()
        st.rerun()

def display_data_info(data):
    """データ情報をサイドバーに表示"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📅 Data Info")
    st.sidebar.info(f"最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # データソースの表示
    if any(not df.empty for df in data.values()):
        # 実データが存在するかチェック
        has_real_data = any(len(df) > 50 for df in data.values() if not df.empty)
        if has_real_data:
            st.sidebar.success("📊 実際のNBAデータを使用")
        else:
            st.sidebar.info("🧪 サンプルデータを使用")
    
    if 'per_game' in data and not data['per_game'].empty:
        st.sidebar.info(f"チーム数: {len(data['per_game'])} teams")
    
    if 'advanced' in data and not data['advanced'].empty:
        player_count = len(data['advanced'][data['advanced']['Player'].notna()]) if 'Player' in data['advanced'].columns else 0
        if player_count > 0:
            st.sidebar.info(f"プレイヤー数: {player_count} players")
    
    if 'player_salaries' in data and not data['player_salaries'].empty:
        st.sidebar.success("✅ プレイヤーサラリーデータあり")
    else:
        st.sidebar.warning("⚠️ サンプルサラリーデータを使用")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"🚨 アプリケーション起動エラー: {e}")
        st.write("エラー詳細:", str(e))