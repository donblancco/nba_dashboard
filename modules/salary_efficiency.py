import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from config import PLOTLY_AVAILABLE, safe_plotly_chart, format_currency
from utils.helpers import filter_multi_team_records

def create_page(data):
    """サラリー効率分析ページ（ゲーム数フィルタリング対応版）"""
    st.header("💰 Player Salary Efficiency Analysis")
    
    st.info("""
    **💰 サラリー効率分析について**
    
    選手の年俸と成績の効率性を分析し、コストパフォーマンスを評価します：
    - **効率指標**: 統計値を年俸で割った効率スコア（統計/100万ドル）
    - **ゲーム数フィルタ**: 一定以上の試合出場選手のみを対象
    - **多角的評価**: 得点、リバウンド、アシストなど複数の指標で分析
    - **投資効果**: どの選手が年俸に見合った、またはそれ以上の成果を出しているかを可視化
    """)
    st.divider()
    
    if 'advanced' not in data or data['advanced'].empty:
        st.error("アドバンスト統計データが見つかりません")
        return
    
    # プレイヤーデータのみを抽出
    df = filter_multi_team_records(data['advanced'].copy())
    player_df = df[df['Player'].notna()] if 'Player' in df.columns else pd.DataFrame()
    
    if player_df.empty:
        st.error("プレイヤーデータが見つかりません")
        return
    
    st.success(f"📊 {len(player_df)} プレイヤーのデータを確認しました")
    
    # サラリーデータの処理（強化版）
    merged_df = process_salary_data_enhanced(data, player_df)
    
    if merged_df.empty:
        st.error("❌ データの処理に失敗しました")
        return
    
    # フィルタリング（ゲーム数対応）
    merged_df = apply_game_based_filters(merged_df)
    
    if merged_df.empty:
        st.error("❌ フィルタリング後にデータがありません")
        return
    
    # 効率分析
    create_efficiency_analysis(merged_df)

def process_salary_data_enhanced(data, player_df):
    """強化されたサラリーデータ処理"""
    use_real_salary = False
    merged_df = pd.DataFrame()
    
    if 'player_salaries' in data and not data['player_salaries'].empty:
        salary_df = data['player_salaries'].copy()
        st.info(f"💰 {len(salary_df)} プレイヤーのサラリーデータを確認中...")
        
        # サラリーデータの構造を詳細分析
        st.write("🔍 サラリーデータの構造分析:")
        st.write(f"カラム: {list(salary_df.columns)}")
        st.write("サンプルデータ:")
        st.dataframe(salary_df.head())
        
        # プレイヤー名カラムを特定
        salary_player_col = identify_player_column(salary_df)
        
        # サラリーカラムを特定
        salary_col = identify_salary_column(salary_df)
        
        if salary_player_col and salary_col:
            st.write(f"✅ 特定されたカラム: プレイヤー名='{salary_player_col}', サラリー='{salary_col}'")
            
            # 強化されたマージを試行
            merged_df = attempt_enhanced_merge(player_df, salary_df, salary_player_col, salary_col)
            
            if not merged_df.empty:
                use_real_salary = True
                st.success(f"✅ {len(merged_df)} プレイヤーのサラリーデータをマージしました")
            else:
                st.warning("❌ 強化マージも失敗。サンプルデータを使用します。")
        else:
            st.warning(f"❌ 適切なカラムが特定できません")
    
    # サンプルデータを使用（実際のデータがマージできない場合）
    if not use_real_salary or merged_df.empty:
        st.info("🧪 サンプルサラリーデータを作成中...")
        merged_df = create_sample_salary_data_with_games(player_df)
    
    return merged_df

def create_sample_salary_data_with_games(player_df):
    """ゲーム数を含むサンプルサラリーデータの作成"""
    np.random.seed(42)
    players = player_df['Player'].unique()
    
    sample_data = []
    for player in players:
        player_stats = player_df[player_df['Player'] == player].iloc[0]
        
        # ゲーム数の生成（現実的な範囲）
        games_played = np.random.randint(20, 82)  # NBAは最大82ゲーム
        
        # 出場時間の生成（ゲーム数に基づく）
        minutes_per_game = np.random.uniform(15, 40)
        total_minutes = games_played * minutes_per_game
        
        # パフォーマンス指標
        per_value = pd.to_numeric(player_stats.get('PER', 15), errors='coerce')
        per_value = per_value if not pd.isna(per_value) else 15
        
        # サラリー計算（ゲーム数とパフォーマンスに基づく）
        base_salary = 2000000
        game_bonus = games_played * 50000  # ゲーム出場ボーナス
        performance_bonus = per_value * 400000
        
        # スター選手ボーナス
        star_bonus = 0
        if any(name in str(player) for name in ['LeBron', 'Stephen', 'Giannis', 'Luka']):
            star_bonus = np.random.uniform(20000000, 30000000)
        elif any(name in str(player) for name in ['Kevin', 'Joel', 'Nikola', 'Jayson']):
            star_bonus = np.random.uniform(10000000, 20000000)
        
        # 最終サラリー
        salary = base_salary + game_bonus + performance_bonus + star_bonus + np.random.uniform(-2000000, 5000000)
        salary = max(salary, 1000000)  # 最低保証
        salary = min(salary, 60000000)  # 上限
        
        sample_data.append({
            'Player': player,
            'Games_Played': games_played,
            'Minutes_Per_Game': round(minutes_per_game, 1),
            'Total_Minutes': round(total_minutes, 0),
            'current_salary': int(salary),
            'PER': per_value,
            'Tm': player_stats.get('Tm', 'N/A')
        })
    
    salary_df = pd.DataFrame(sample_data)
    
    # 元のプレイヤーデータとマージ
    merged_df = player_df.merge(salary_df[['Player', 'current_salary']], 
                               on='Player', how='inner')
    merged_df['Salary'] = merged_df['current_salary']
    
    st.success(f"✅ {len(merged_df)} プレイヤーのサンプルデータを作成しました（ゲーム数含む）")
    return merged_df

def apply_game_based_filters(merged_df):
    """ゲーム数ベースのフィルタリングの適用"""
    st.subheader("🔧 フィルタリングオプション")
    col1, col2 = st.columns(2)
    
    with col1:
        # 最低ゲーム数でフィルタリング
        if 'G' in merged_df.columns:
            min_games = st.slider(
                "最低ゲーム数", 
                min_value=10, 
                max_value=82, 
                value=25,
                help="指定したゲーム数以上プレイしたプレイヤーのみを表示"
            )
            merged_df['G_numeric'] = pd.to_numeric(merged_df['G'], errors='coerce').fillna(0)
            merged_df = merged_df[merged_df['G_numeric'] >= min_games]
            st.write(f"ゲーム数フィルタ後: {len(merged_df)} プレイヤー")
        else:
            # Gカラムがない場合はMPベースでフィルタリング
            if 'MP' in merged_df.columns:
                min_minutes = st.slider("最低出場時間 (分/試合)", 5, 35, 15)
                merged_df['MP_numeric'] = pd.to_numeric(merged_df['MP'], errors='coerce').fillna(0)
                merged_df = merged_df[merged_df['MP_numeric'] >= min_minutes]
                st.write(f"出場時間フィルタ後: {len(merged_df)} プレイヤー")
    
    with col2:
        # サラリー範囲でフィルタリング
        if len(merged_df) > 0:
            min_salary = int(merged_df['Salary'].min())
            max_salary = int(merged_df['Salary'].max())
            if min_salary < max_salary:
                salary_range = st.slider(
                    "サラリー範囲 (Million Dollar)",
                    min_value=min_salary//1000000,
                    max_value=max_salary//1000000,
                    value=(min_salary//1000000, max_salary//1000000),
                    help="指定したサラリー範囲内のプレイヤーのみを表示"
                )
                merged_df = merged_df[
                    (merged_df['Salary'] >= salary_range[0] * 1000000) &
                    (merged_df['Salary'] <= salary_range[1] * 1000000)
                ]
                st.write(f"サラリーフィルタ後: {len(merged_df)} プレイヤー")
    
    return merged_df

def create_efficiency_analysis(merged_df):
    """効率分析の実行"""
    # 効率指標の選択
    available_metrics = get_available_metrics(merged_df)
    
    if not available_metrics:
        st.error("❌ 利用可能な効率指標が見つかりません")
        return
    
    st.subheader("📊 効率分析設定")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_metric = st.selectbox(
            "効率指標を選択:",
            options=available_metrics,
            format_func=lambda x: {
                'PER': 'PER (Player Efficiency Rating)',
                'VORP': 'VORP (Value Over Replacement Player)',
                'WS': 'WS (Win Shares)',
                'BPM': 'BPM (Box Plus/Minus)',
                'TS%': 'TS% (True Shooting %)',
                'USG%': 'USG% (Usage Rate)'
            }.get(x, x)
        )
    
    with col2:
        display_count = st.selectbox("表示するプレイヤー数:", [10, 15, 20, 25], index=0)
    
    # 効率計算
    efficiency_col = selected_metric + '_per_million'
    metric_values = pd.to_numeric(merged_df[selected_metric], errors='coerce').fillna(0)
    merged_df[efficiency_col] = (metric_values / merged_df['Salary']) * 1000000
    
    # データクリーニング
    merged_df = merged_df[merged_df[efficiency_col].notna()]
    merged_df = merged_df[merged_df[efficiency_col] != float('inf')]
    merged_df = merged_df[merged_df[efficiency_col] > 0]
    
    if merged_df.empty:
        st.error("❌ 効率計算後にデータがありません")
        return
    
    # ランキング表示
    display_ranking_table_with_games(merged_df, selected_metric, efficiency_col, display_count)
    
    # 可視化
    if PLOTLY_AVAILABLE:
        create_visualizations_with_games(merged_df, selected_metric, efficiency_col)
    
    # サマリーとインサイト
    display_summary_and_insights_with_games(merged_df, selected_metric, efficiency_col)

def display_ranking_table_with_games(merged_df, selected_metric, efficiency_col, display_count):
    """ゲーム数を含むランキングテーブルの表示"""
    top_players = merged_df.nlargest(display_count, efficiency_col)
    
    st.subheader(f"🏆 Top {display_count} プレイヤー効率ランキング")
    
    ranking_data = []
    for i, (_, player) in enumerate(top_players.iterrows(), 1):
        # ゲーム数の安全な取得
        games_played = player.get('G', 'N/A')
        if games_played != 'N/A':
            games_played = int(games_played) if pd.notna(games_played) else 'N/A'
        
        # 出場時間の安全な取得
        mp_per_game = player.get('MP', 0)
        mp_per_game = pd.to_numeric(mp_per_game, errors='coerce')
        mp_per_game = mp_per_game if not pd.isna(mp_per_game) else 0
        
        metric_value = pd.to_numeric(player[selected_metric], errors='coerce')
        metric_value = metric_value if not pd.isna(metric_value) else 0
        
        ranking_data.append({
            'Rank': i,
            'Player': player['Player'],
            'Team': player.get('Team', 'N/A'),
            'Games': games_played,
            'Min/Game': round(mp_per_game, 1),
            selected_metric: round(metric_value, 3),
            'Salary (M)': round(player['Salary'] / 1000000, 2),
            'Efficiency': round(player[efficiency_col], 8)
        })
    
    ranking_df = pd.DataFrame(ranking_data)
    
    # 美しいテーブル表示
    st.dataframe(
        ranking_df.style
        .format({
            'Efficiency': '{:.8f}',
            'Salary (M)': '${:.2f}M',
            'Min/Game': '{:.1f}',
            selected_metric: '{:.3f}'
        })
        .background_gradient(subset=['Efficiency'], cmap='RdYlGn')
        .highlight_max(subset=['Efficiency'], color='lightgreen')
        .set_properties(**{
            'text-align': 'center',
            'font-size': '12px'
        }),
        use_container_width=True
    )

def create_visualizations_with_games(merged_df, selected_metric, efficiency_col):
    """ゲーム数を考慮した可視化の作成"""
    st.subheader("📊 可視化分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Top 10 効率ランキング**")
        chart_data = merged_df.nlargest(10, efficiency_col)
        
        fig1 = px.bar(
            chart_data,
            x=efficiency_col,
            y='Player',
            orientation='h',
            title=f'Top 10 - {selected_metric} per Million Dollar',
            labels={efficiency_col: f'{selected_metric} per Million Dollar'},
            color=efficiency_col,
            color_continuous_scale='Viridis',
            hover_data=['G'] if 'G' in chart_data.columns else None
        )
        fig1.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        safe_plotly_chart(fig1)
    
    with col2:
        st.write("**効率 vs ゲーム数関係**")
        
        # ゲーム数がある場合はゲーム数を、ない場合はサラリーを使用
        if 'G' in merged_df.columns:
            x_axis = 'G'
            x_label = 'Games Played'
            title = f'{selected_metric} vs Games Played'
        else:
            x_axis = 'Salary'
            x_label = 'Salary (Dollar)'
            title = f'{selected_metric} vs Salary'
        
        fig2 = px.scatter(
            merged_df,
            x=x_axis,
            y=selected_metric,
            hover_data=['Player', 'Team'] if 'Team' in merged_df.columns else ['Player'],
            title=title,
            labels={
                x_axis: x_label,
                selected_metric: selected_metric
            },
            color=efficiency_col,
            color_continuous_scale='Viridis',
            size='Salary',
            size_max=15
        )
        
        fig2.update_layout(height=500)
        if x_axis == 'Salary':
            fig2.update_layout(xaxis_tickformat='$,.0f')
        
        safe_plotly_chart(fig2)

def display_summary_and_insights_with_games(merged_df, selected_metric, efficiency_col):
    """ゲーム数を含むサマリーとインサイトの表示"""
    st.subheader("📈 サマリー統計")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("分析プレイヤー数", len(merged_df))
    
    with col2:
        avg_salary = merged_df['Salary'].mean()
        st.metric("平均サラリー", format_currency(avg_salary))
    
    with col3:
        if 'G' in merged_df.columns:
            avg_games = pd.to_numeric(merged_df['G'], errors='coerce').mean()
            st.metric("平均ゲーム数", f"{avg_games:.1f}")
        else:
            avg_efficiency = merged_df[efficiency_col].mean()
            st.metric(f"平均{selected_metric}効率", f"{avg_efficiency:.6f}")
    
    with col4:
        best_player = merged_df.loc[merged_df[efficiency_col].idxmax(), 'Player']
        st.metric("最高効率プレイヤー", best_player)
    
    # インサイト
    st.subheader("💡 注目ポイント")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 多ゲーム出場プレイヤーの効率
        if 'G' in merged_df.columns:
            merged_df['G_numeric'] = pd.to_numeric(merged_df['G'], errors='coerce').fillna(0)
            high_games_threshold = merged_df['G_numeric'].quantile(0.75)
            high_games_players = merged_df[merged_df['G_numeric'] >= high_games_threshold]
            
            if not high_games_players.empty:
                best_durable = high_games_players.loc[high_games_players[efficiency_col].idxmax()]
                st.success(
                    f"🏃 **耐久性+効率MVP**: {best_durable['Player']}\n\n"
                    f"ゲーム数: {int(best_durable['G_numeric'])} | "
                    f"効率: {best_durable[efficiency_col]:.6f}"
                )
        else:
            # バリュー契約プレイヤー
            value_threshold = merged_df['Salary'].quantile(0.3)
            value_players = merged_df[merged_df['Salary'] <= value_threshold]
            
            if not value_players.empty:
                best_value = value_players.loc[value_players[efficiency_col].idxmax()]
                st.success(
                    f"🌟 **バリュー契約MVP**: {best_value['Player']}\n\n"
                    f"サラリー: ${best_value['Salary']/1000000:.1f}M | "
                    f"効率: {best_value[efficiency_col]:.6f}"
                )
    
    with col2:
        # 高額契約の効率プレイヤー
        expensive_threshold = merged_df['Salary'].quantile(0.8)
        expensive_players = merged_df[merged_df['Salary'] >= expensive_threshold]
        
        if not expensive_players.empty:
            best_expensive = expensive_players.loc[expensive_players[efficiency_col].idxmax()]
            games_info = f" | {int(pd.to_numeric(best_expensive.get('G', 0), errors='coerce'))}試合" if 'G' in merged_df.columns else ""
            st.info(
                f"💰 **高額契約で最も効率的**: {best_expensive['Player']}\n\n"
                f"サラリー: ${best_expensive['Salary']/1000000:.1f}M{games_info} | "
                f"効率: {best_expensive[efficiency_col]:.6f}"
            )

# ヘルパー関数（変更なし）
def identify_player_column(salary_df):
    """プレイヤー名カラムを特定"""
    possible_names = ['player_name', 'Player', 'name', 'player', 'NAME', 'full_name']
    
    for col in possible_names:
        if col in salary_df.columns:
            sample_values = salary_df[col].dropna().head()
            if len(sample_values) > 0:
                try:
                    pd.to_numeric(sample_values.iloc[0])
                    continue
                except:
                    return col
    
    for col in salary_df.columns:
        try:
            pd.to_numeric(salary_df[col].dropna().iloc[0])
        except:
            return col
    
    return None

def identify_salary_column(salary_df):
    """サラリーカラムを特定"""
    possible_names = ['current_salary', 'salary', 'total_salary', '2024-25', '2025', 'amount']
    
    for col in possible_names:
        if col in salary_df.columns:
            return col
    
    numeric_cols = salary_df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        max_avg = 0
        best_col = None
        for col in numeric_cols:
            avg_val = salary_df[col].mean()
            if avg_val > max_avg:
                max_avg = avg_val
                best_col = col
        return best_col
    
    return None

def attempt_enhanced_merge(player_df, salary_df, salary_player_col, salary_col):
    """強化されたマージ処理"""
    salary_df_clean = salary_df.copy()
    player_df_clean = player_df.copy()
    
    if salary_player_col in salary_df_clean.columns:
        salary_df_clean[salary_player_col] = salary_df_clean[salary_player_col].astype(str).str.strip()
    
    player_df_clean['Player'] = player_df_clean['Player'].astype(str).str.strip()
    salary_df_clean[salary_col] = pd.to_numeric(salary_df_clean[salary_col], errors='coerce')
    
    merged_df = player_df_clean.merge(
        salary_df_clean[[salary_player_col, salary_col]], 
        left_on='Player', 
        right_on=salary_player_col, 
        how='inner'
    )
    
    if not merged_df.empty:
        merged_df['Salary'] = merged_df[salary_col]
        merged_df = merged_df[merged_df['Salary'].notna() & (merged_df['Salary'] > 0)]
        return merged_df
    
    return pd.DataFrame()

def get_available_metrics(merged_df):
    """利用可能な効率指標を取得"""
    available_metrics = []
    for metric in ['PER', 'VORP', 'WS', 'BPM', 'TS%', 'USG%']:
        if metric in merged_df.columns:
            metric_values = pd.to_numeric(merged_df[metric], errors='coerce')
            if not metric_values.isna().all() and metric_values.sum() != 0:
                available_metrics.append(metric)
    return available_metrics