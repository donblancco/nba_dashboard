import streamlit as st
import os
import sys
from datetime import datetime

# App Runner環境の検出
IS_APP_RUNNER = 'AWS_REGION' in os.environ and 'PORT' in os.environ

# ページ設定（App Runnerでは最初に一度だけ設定）
if not hasattr(st.session_state, 'page_config_set'):
    st.set_page_config(
        page_title="NBA 2024-25 Analytics Dashboard",
        page_icon="🏀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.session_state.page_config_set = True

# App Runner用のCSS設定
if IS_APP_RUNNER:
    st.markdown("""
    <style>
    /* App Runner用の最適化CSS */
    
    /* ナビゲーション完全非表示 */
    div[data-testid="stSidebarNav"],
    div[data-testid="stSidebarNavSeparator"],
    div[data-testid="stHeader"],
    header[data-testid="stHeader"],
    .stAppHeader,
    .css-1d391kg,
    .css-1dp5vir,
    .css-18e3th9,
    .css-1rs6os,
    .css-1v0mbdj,
    .e16nr0p34 {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        width: 0px !important;
    }
    
    /* メインコンテンツの調整 */
    .main .block-container {
        padding-top: 1rem !important;
        max-width: 1200px !important;
    }
    
    /* App Runner用のパフォーマンス最適化 */
    .stDataFrame {
        max-height: 600px !important;
        overflow-y: auto !important;
    }
    
    /* モバイル対応 */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
    
    /* ローディング改善 */
    .stSpinner {
        border-color: #FF6B35 !important;
    }
    
    /* メトリクスカードの最適化 */
    div[data-testid="metric-container"] {
        background-color: white !important;
        border: 1px solid #e0e0e0 !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    /* App Runner環境表示 */
    .app-runner-badge {
        position: fixed;
        top: 10px;
        right: 10px;
        background: linear-gradient(45deg, #FF6B35, #F7931E);
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        z-index: 1000;
    }
    </style>
    
    <div class="app-runner-badge">
        🚀 AWS App Runner
    </div>
    """, unsafe_allow_html=True)

# モジュールのインポート（エラーハンドリング強化）
try:
    # modules ディレクトリが存在するかチェック
    if os.path.exists('modules'):
        sys.path.insert(0, 'modules')
        
    from modules import (
        team_overview,
        scoring_analysis,
        advanced_analytics,
        team_comparison,
        correlation_analysis,
        data_explorer,
        salary_efficiency
    )
    MODULES_LOADED = True
except ImportError as e:
    st.error(f"❌ モジュールのインポートに失敗しました: {e}")
    st.info("📁 ファイル構造を確認してください。modules/ ディレクトリが存在し、必要なファイルが含まれている必要があります。")
    MODULES_LOADED = False

# データローダーのインポート
try:
    from data.loader import load_nba_data
    DATA_LOADER_AVAILABLE = True
except ImportError:
    # データローダーがない場合はサンプルデータを使用
    from data.sample_data import create_sample_data
    DATA_LOADER_AVAILABLE = False

def load_data_safely():
    """安全なデータ読み込み"""
    try:
        if DATA_LOADER_AVAILABLE:
            return load_nba_data()
        else:
            return create_sample_data()
    except Exception as e:
        st.warning(f"⚠️ データ読み込みエラー: {e}")
        # フォールバック: 基本的なサンプルデータ
        return create_basic_sample_data()

def create_basic_sample_data():
    """基本的なサンプルデータ作成（フォールバック用）"""
    import pandas as pd
    import numpy as np
    
    np.random.seed(42)
    teams = ['LAL', 'BOS', 'GSW', 'MIA', 'CHI', 'NYK', 'BRK', 'PHI', 'MIL', 'DEN']
    
    # 基本的なper_gameデータ
    per_game_data = []
    for team in teams:
        per_game_data.append({
            'Team': team,
            'PTS': round(110 + np.random.uniform(-10, 15), 1),
            'FG%': round(0.450 + np.random.uniform(-0.05, 0.05), 3),
            '3P%': round(0.350 + np.random.uniform(-0.05, 0.05), 3),
            'REB': round(45 + np.random.uniform(-5, 8), 1),
            'AST': round(25 + np.random.uniform(-5, 8), 1),
            'STL': round(8 + np.random.uniform(-2, 3), 1),
            'BLK': round(5 + np.random.uniform(-2, 3), 1),
            'TOV': round(14 + np.random.uniform(-3, 4), 1)
        })
    
    return {
        'per_game': pd.DataFrame(per_game_data),
        'advanced': pd.DataFrame(),
        'play_by_play': pd.DataFrame(),
        'team_salaries': pd.DataFrame(),
        'player_salaries': pd.DataFrame()
    }

def main():
    """メインアプリケーション"""
    
    # ヘルスチェック用のエンドポイント
    if st.query_params.get('health'):
        st.success("✅ App is healthy")
        return
    
    # タイトルと環境情報
    st.title("🏀 NBA 2024-25 Analytics Dashboard")
    
    if IS_APP_RUNNER:
        st.info("🚀 AWS App Runner で実行中 - 自動スケーリング対応")
    
    st.markdown("---")
    
    # モジュールが読み込めない場合の対応
    if not MODULES_LOADED:
        st.error("❌ アプリケーションモジュールが見つかりません")
        st.markdown("""
        ### 🔧 トラブルシューティング
        
        1. **ファイル構造の確認**:
           ```
           nba-dashboard/
           ├── app.py
           ├── modules/
           │   ├── __init__.py
           │   ├── team_overview.py
           │   └── ...
           └── data/
           ```
        
        2. **必要なファイルの存在確認**
        3. **GitHub リポジトリの再デプロイ**
        """)
        return
    
    # データ読み込み（キャッシュ付き）
    with st.spinner("📊 データを読み込み中..."):
        data = load_data_safely()
    
    # ナビゲーション
    st.sidebar.title("📊 Navigation")
    
    page_options = {
        "🏠 Team Overview": team_overview,
        "📊 Scoring Analysis": scoring_analysis,
        "⚖️ Team Comparison": team_comparison,
        "📈 Advanced Analytics": advanced_analytics,
        "💰 Salary Efficiency": salary_efficiency,
        "🔗 Correlation Analysis": correlation_analysis,
        "🔍 Data Explorer": data_explorer
    }
    
    selected_page = st.sidebar.selectbox(
        "分析ページを選択:",
        options=list(page_options.keys()),
        key="page_selector"
    )
    
    # App Runner用のパフォーマンス情報
    if IS_APP_RUNNER:
        with st.sidebar.expander("⚡ パフォーマンス情報"):
            st.write(f"🖥️ CPU: {os.environ.get('AWS_EXECUTION_ENV', 'Unknown')}")
            st.write(f"📍 Region: {os.environ.get('AWS_REGION', 'Unknown')}")
            st.write(f"🔄 Auto Scaling: 有効")
    
    # データ情報表示
    display_data_info(data)
    
    # 選択されたページを表示
    try:
        with st.container():
            page_module = page_options[selected_page]
            page_module.create_page(data)
    except Exception as e:
        st.error(f"❌ ページ表示エラー: {e}")
        
        # App Runner用のエラー詳細
        with st.expander("🔍 エラーの詳細"):
            st.code(str(e))
            st.write("**環境情報:**")
            st.write(f"- Python バージョン: {sys.version}")
            st.write(f"- Streamlit バージョン: {st.__version__}")
            st.write(f"- App Runner: {IS_APP_RUNNER}")
    
    # フッター
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 データ再読み込み"):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if IS_APP_RUNNER:
            st.info("☁️ クラウドで実行中")
        else:
            st.info("💻 ローカルで実行中")
    
    with col3:
        st.write(f"⏰ {datetime.now().strftime('%H:%M:%S')}")

def display_data_info(data):
    """データ情報表示（App Runner最適化）"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📅 Data Info")
    st.sidebar.info(f"最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # データセット情報（簡潔に表示）
    total_records = 0
    for key, df in data.items():
        if not df.empty:
            records = len(df)
            total_records += records
            if records > 0:
                st.sidebar.success(f"✅ {key}: {records}")
        else:
            st.sidebar.warning(f"❌ {key}: Empty")
    
    # 総計表示
    if total_records > 0:
        st.sidebar.metric("📊 総レコード数", total_records)
    
    # App Runner固有の情報
    if IS_APP_RUNNER:
        st.sidebar.markdown("### 🚀 App Runner")
        st.sidebar.success("自動スケーリング有効")
        
        # 簡単なメモリ使用量表示（概算）
        import psutil
        try:
            memory_percent = psutil.virtual_memory().percent
            st.sidebar.metric("💾 メモリ使用率", f"{memory_percent:.1f}%")
        except:
            pass

# メイン実行
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"🚨 アプリケーション起動エラー: {e}")
        
        # App Runner用のエラー情報
        st.markdown("""
        ### 🔧 App Runner トラブルシューティング
        
        1. **ログの確認**: AWS CloudWatch でアプリケーションログを確認
        2. **リソース確認**: メモリ・CPU使用量を確認
        3. **再デプロイ**: GitHub の最新コミットで再デプロイ
        4. **設定確認**: apprunner.yaml の設定を確認
        """)
        
        with st.expander("🔍 詳細なエラー情報"):
            st.code(str(e))
            st.write("**システム情報:**")
            st.write(f"- Python: {sys.version}")
            st.write(f"- Streamlit: {st.__version__}")
            st.write(f"- 作業ディレクトリ: {os.getcwd()}")
            st.write(f"- 環境変数: {list(os.environ.keys())[:10]}...")  # セキュリティのため一部のみ表示