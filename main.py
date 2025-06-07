import streamlit as st
from datetime import datetime
import sys
import traceback

# 設定の初期化（一度だけ実行）
if 'config_setup' not in st.session_state:
    try:
        from config import setup_page_config
        setup_page_config()
        st.session_state.config_setup = True
    except Exception as e:
        st.error(f"設定の初期化に失敗しました: {e}")

# データローダーのインポート
try:
    from data.loader import load_nba_data
except ImportError as e:
    st.error(f"データローダーのインポートに失敗しました: {e}")
    st.stop()

# ページモジュールの安全なインポート
page_modules = {}
page_names = [
    'team_overview',
    'scoring_analysis',
    'team_comparison',
    'advanced_analytics',
    'salary_efficiency',
    'correlation_analysis',
    'data_explorer'
]

for page_name in page_names:
    try:
        module = __import__(f'pages.{page_name}', fromlist=[page_name])
        page_modules[page_name] = module
    except ImportError as e:
        st.warning(f"ページ '{page_name}' のインポートに失敗しました: {e}")
        page_modules[page_name] = None

def main():
    """メインアプリケーション"""
    
    # タイトル（設定でヘッダーが非表示になっているのでここで表示）
    st.title("🏀 NBA 2024-25 Analytics Dashboard")
    st.markdown("---")
    
    # データ読み込み（サイレント）
    try:
        data = load_nba_data()
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {e}")
        st.stop()
    
    # サイドバーナビゲーション
    st.sidebar.title("📊 Navigation")
    
    # 利用可能なページのリストを作成
    available_pages = []
    page_display_names = {
        'team_overview': "Team Overview",
        'scoring_analysis': "Scoring Analysis", 
        'team_comparison': "Team Comparison",
        'advanced_analytics': "Advanced Analytics",
        'salary_efficiency': "Salary Efficiency",
        'correlation_analysis': "Correlation Analysis",
        'data_explorer': "Data Explorer"
    }
    
    for page_name in page_names:
        if page_modules[page_name] is not None:
            available_pages.append(page_display_names[page_name])
    
    if not available_pages:
        st.error("利用可能なページがありません")
        st.stop()
    
    page = st.sidebar.selectbox(
        "分析ページを選択:",
        available_pages
    )
    
    # データ情報表示
    display_data_info(data)
    
    # ページルーティング
    try:
        # 表示名から内部名への変換
        page_internal_name = None
        for internal, display in page_display_names.items():
            if display == page:
                page_internal_name = internal
                break
        
        if page_internal_name and page_modules[page_internal_name]:
            page_modules[page_internal_name].create_page(data)
        else:
            st.error(f"ページ '{page}' を表示できません")
            
    except Exception as e:
        st.error(f"ページ表示エラー: {e}")
        with st.expander("エラーの詳細"):
            st.code(traceback.format_exc())
    
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
    
    # データセット情報
    dataset_info = []
    for key, df in data.items():
        if not df.empty:
            dataset_info.append(f"✅ {key}: {len(df)} records")
        else:
            dataset_info.append(f"❌ {key}: No data")
    
    if dataset_info:
        st.sidebar.markdown("**データセット:**")
        for info in dataset_info:
            if "✅" in info:
                st.sidebar.success(info)
            else:
                st.sidebar.warning(info)
    
    # 追加情報
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
        with st.expander("エラーの詳細"):
            st.code(traceback.format_exc())
        st.write("**解決方法:**")
        st.write("1. 必要なライブラリがインストールされているか確認")
        st.write("2. ファイル構造が正しいか確認")
        st.write("3. config.py ファイルが存在するか確認")