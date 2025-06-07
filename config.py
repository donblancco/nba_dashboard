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
    
    # 不要なUI要素を非表示にするCSS
    st.markdown("""
    <style>
        /* ファイル一覧ナビゲーションを非表示 */
        div[data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        /* ナビゲーションの区切り線も非表示 */
        div[data-testid="stSidebarNavSeparator"] {
            display: none !important;
        }
        
        /* サイドバーの上部調整 */
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem;
        }
        
        /* Streamlitメニューとフッターを非表示 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Deploy ボタンを非表示 */
        .css-1rs6os {display: none;}
        
        /* ページタイトルのスタイリング */
        .main h1 {
            color: #1f1f1f;
            font-weight: 700;
            margin-bottom: 2rem;
        }
        
        /* サイドバータイトルのスタイリング */
        .css-1lcbmhc h1 {
            font-size: 1.5rem;
            color: #262730;
            margin-bottom: 1rem;
        }
    </style>
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