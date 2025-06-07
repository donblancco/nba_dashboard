import streamlit as st

# エラーハンドリング付きインポート
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError as e:
    st.warning(f"Plotlyインポートエラー: {e}")
    PLOTLY_AVAILABLE = False

try:
    import json
    JSON_AVAILABLE = True
except ImportError as e:
    st.warning(f"JSONインポートエラー: {e}")
    JSON_AVAILABLE = False

def setup_page_config():
    """Streamlitページ設定"""
    st.set_page_config(
        page_title="NBA 2024-25 Analytics Dashboard",
        page_icon="🏀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 超強力なナビゲーション非表示CSS（ページ遷移対応）
    st.markdown("""
    <style>
        /* ====== 最優先・即座に適用される非表示CSS ====== */
        
        /* ページ読み込み開始と同時に非表示 */
        * {
            --hide-nav: none !important;
        }
        
        /* ====== すべてのナビゲーション要素を即座に非表示 ====== */
        
        /* ファイル名・アプリ名を含むすべてのヘッダー */
        div[data-testid="stSidebarNav"],
        div[data-testid="stSidebarNavSeparator"],
        div[data-testid="stHeader"],
        header[data-testid="stHeader"],
        .stAppHeader,
        .css-1d391kg,
        .css-1dp5vir,
        .css-18e3th9,
        .css-1rs6os,
        .css-k1ih3n,
        .css-1v0mbdj,
        .e16nr0p34,
        .css-1vbkxwb,
        .css-17lntkn,
        .e1fqkh3o0,
        .e1fqkh3o1,
        .e1fqkh3o2,
        .stToolbar,
        .viewerBadge_container__1QSob,
        div[data-testid="stDecoration"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0px !important;
            min-height: 0px !important;
            max-height: 0px !important;
            width: 0px !important;
            min-width: 0px !important;
            max-width: 0px !important;
            padding: 0px !important;
            margin: 0px !important;
            border: none !important;
            overflow: hidden !important;
            position: absolute !important;
            left: -9999px !important;
            top: -9999px !important;
        }
        
        /* ====== サイドバー内のナビゲーション完全削除 ====== */
        
        /* サイドバーのすべてのナビゲーション要素 */
        section[data-testid="stSidebar"] > div:first-child > div:first-child,
        section[data-testid="stSidebar"] > div > div > div > ul,
        section[data-testid="stSidebar"] .css-1v0mbdj,
        section[data-testid="stSidebar"] .e16nr0p34,
        section[data-testid="stSidebar"] nav,
        section[data-testid="stSidebar"] [role="navigation"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            overflow: hidden !important;
        }
        
        /* ====== ページ遷移時の一時的表示防止 ====== */
        
        /* アニメーション中も非表示 */
        .css-1v0mbdj,
        .e16nr0p34,
        [data-testid="stSidebarNav"] {
            transition: none !important;
            animation: none !important;
            display: none !important;
        }
        
        /* ページ読み込み中の非表示 */
        body.loading .css-1v0mbdj,
        body.loading .e16nr0p34,
        body.loading [data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        /* ====== レイアウト修復 ====== */
        
        /* サイドバーの上部スペース調整 */
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem !important;
            margin-top: 0 !important;
        }
        
        /* メインコンテンツの上部調整 */
        .main .block-container {
            padding-top: 1rem !important;
            margin-top: 0 !important;
        }
        
        /* アプリ全体の上部マージン削除 */
        .stApp {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        /* ====== その他のUI改善 ====== */
        
        /* Streamlitメニュー・フッター非表示 */
        #MainMenu {
            visibility: hidden !important;
            display: none !important;
        }
        
        footer {
            visibility: hidden !important;
            display: none !important;
        }
        
        /* ページタイトルのスタイリング */
        .main h1 {
            color: #1f1f1f !important;
            font-weight: 700 !important;
            margin-bottom: 2rem !important;
            margin-top: 0 !important;
        }
        
        /* サイドバータイトルのスタイリング */
        .css-1lcbmhc h1 {
            font-size: 1.5rem !important;
            color: #262730 !important;
            margin-bottom: 1rem !important;
        }
        
        /* メトリクスカードのスタイリング */
        div[data-testid="metric-container"] {
            background-color: white !important;
            border: 1px solid #e0e0e0 !important;
            padding: 1rem !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        /* データフレームのスタイリング */
        .stDataFrame {
            border-radius: 8px !important;
            overflow: hidden !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
    </style>
    
    <!-- ページ遷移対応JavaScript -->
    <script>
    // 即座に実行される非表示関数
    function forceHideNavigation() {
        const selectors = [
            'div[data-testid="stSidebarNav"]',
            'div[data-testid="stSidebarNavSeparator"]', 
            'div[data-testid="stHeader"]',
            'header[data-testid="stHeader"]',
            '.css-1v0mbdj',
            '.e16nr0p34',
            '.css-1d391kg',
            '.css-1dp5vir',
            '.stAppHeader',
            '.css-18e3th9',
            '.css-1rs6os',
            'nav',
            '[role="navigation"]'
        ];
        
        selectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                element.style.cssText = `
                    display: none !important;
                    visibility: hidden !important;
                    opacity: 0 !important;
                    height: 0px !important;
                    width: 0px !important;
                    padding: 0px !important;
                    margin: 0px !important;
                    position: absolute !important;
                    left: -9999px !important;
                    top: -9999px !important;
                `;
            });
        });
    }
    
    // 即座に実行
    forceHideNavigation();
    
    // DOM変更監視（ページ遷移で新しい要素が追加された時）
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                // 新しい要素が追加されたら即座に非表示処理
                setTimeout(forceHideNavigation, 0);
            }
        });
    });
    
    // 監視開始
    if (document.body) {
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    // 定期的な強制実行（保険）
    setInterval(forceHideNavigation, 100);
    
    // ページ読み込み完了時
    document.addEventListener('DOMContentLoaded', forceHideNavigation);
    
    // 遅延実行（Streamlitの遅延読み込み対応）
    setTimeout(forceHideNavigation, 50);
    setTimeout(forceHideNavigation, 100);
    setTimeout(forceHideNavigation, 200);
    setTimeout(forceHideNavigation, 500);
    setTimeout(forceHideNavigation, 1000);
    
    // ページフォーカス時（他のタブから戻ってきた時）
    window.addEventListener('focus', forceHideNavigation);
    
    // リサイズ時（レイアウト変更時）
    window.addEventListener('resize', forceHideNavigation);
    </script>
    """, unsafe_allow_html=True)

def apply_navigation_hiding():
    """各ページで呼び出す追加の非表示処理"""
    st.markdown("""
    <style>
    /* ページ固有の追加非表示CSS */
    div[data-testid="stSidebarNav"],
    .css-1v0mbdj,
    .e16nr0p34 {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    
    <script>
    // ページレベルでの強制非表示
    setTimeout(function() {
        const navElements = document.querySelectorAll('div[data-testid="stSidebarNav"], .css-1v0mbdj, .e16nr0p34');
        navElements.forEach(el => {
            el.style.display = 'none';
            el.style.visibility = 'hidden';
        });
    }, 0);
    </script>
    """, unsafe_allow_html=True)

def safe_plotly_chart(fig, use_container_width=True):
    """安全なPlotlyチャート表示"""
    if not PLOTLY_AVAILABLE:
        st.error("Plotlyが利用できません")
        return
    
    try:
        st.plotly_chart(fig, use_container_width=use_container_width)
    except Exception as e:
        st.error(f"グラフ表示エラー: {e}")
        st.write("エラー詳細:", str(e))

def check_required_columns(df, required_cols, data_name="データ"):
    """必要なカラムが存在するかチェック"""
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"{data_name}に必要なカラムがありません: {missing_cols}")
        st.info(f"利用可能なカラム: {list(df.columns)}")
        
        # デバッグ情報の表示
        with st.expander("🔍 詳細なデバッグ情報"):
            st.write("**データ構造:**")
            st.write(f"- 行数: {len(df)}")
            st.write(f"- 列数: {len(df.columns)}")
            st.write(f"- データ型: {df.dtypes.to_dict()}")
            if len(df) > 0:
                st.write("**サンプルデータ:**")
                st.dataframe(df.head(3))
        return False
    return True

def format_currency(amount):
    """通貨フォーマット"""
    return f"${amount/1000000:.1f}M"

def format_percentage(value):
    """パーセンテージフォーマット"""
    return f"{value:.1%}"

# 共通のカラーパレット
COLOR_PALETTE = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e', 
    'success': '#2ca02c',
    'warning': '#d62728',
    'info': '#17becf'
}

# NBA チーム情報
NBA_TEAMS = {
    'ATL': 'Atlanta Hawks',
    'BOS': 'Boston Celtics',
    'BRK': 'Brooklyn Nets',
    'CHO': 'Charlotte Hornets',
    'CHI': 'Chicago Bulls',
    'CLE': 'Cleveland Cavaliers',
    'DAL': 'Dallas Mavericks',
    'DEN': 'Denver Nuggets',
    'DET': 'Detroit Pistons',
    'GSW': 'Golden State Warriors',
    'HOU': 'Houston Rockets',
    'IND': 'Indiana Pacers',
    'LAC': 'LA Clippers',
    'LAL': 'Los Angeles Lakers',
    'MEM': 'Memphis Grizzlies',
    'MIA': 'Miami Heat',
    'MIL': 'Milwaukee Bucks',
    'MIN': 'Minnesota Timberwolves',
    'NOP': 'New Orleans Pelicans',
    'NYK': 'New York Knicks',
    'OKC': 'Oklahoma City Thunder',
    'ORL': 'Orlando Magic',
    'PHI': 'Philadelphia 76ers',
    'PHX': 'Phoenix Suns',
    'POR': 'Portland Trail Blazers',
    'SAC': 'Sacramento Kings',
    'SAS': 'San Antonio Spurs',
    'TOR': 'Toronto Raptors',
    'UTA': 'Utah Jazz',
    'WAS': 'Washington Wizards'
}