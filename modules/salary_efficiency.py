import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from config import PLOTLY_AVAILABLE, safe_plotly_chart, format_currency

def create_page(data):
    """サラリー効率分析ページ（マージ機能強化版）"""
    st.header("💰 Player Salary Efficiency Analysis")
    
    if 'advanced' not in data or data['advanced'].empty:
        st.error("アドバンスト統計データが見つかりません")
        return
    
    # プレイヤーデータのみを抽出
    df = data['advanced'].copy()
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
    
    # フィルタリング
    merged_df = apply_filters(merged_df)
    
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
        merged_df = create_sample_salary_data(player_df)
    
    return merged_df

def identify_player_column(salary_df):
    """プレイヤー名カラムを特定"""
    possible_names = ['player_name', 'Player', 'name', 'player', 'NAME', 'full_name']
    
    for col in possible_names:
        if col in salary_df.columns:
            # 文字列データかチェック
            sample_values = salary_df[col].dropna().head()
            if len(sample_values) > 0:
                # 数値のみでない場合（プレイヤー名の可能性が高い）
                try:
                    pd.to_numeric(sample_values.iloc[0])
                    continue  # 数値の場合はスキップ
                except:
                    return col  # 数値変換に失敗（文字列）の場合は選択
    
    # 見つからない場合、最初の非数値列を使用
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
    
    # 見つからない場合、最も大きな数値を持つ列を探す
    numeric_cols = salary_df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        # 平均値が最も大きい数値列をサラリー列とする
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
    
    # データクリーニング
    salary_df_clean = salary_df.copy()
    player_df_clean = player_df.copy()
    
    # プレイヤー名の正規化
    if salary_player_col in salary_df_clean.columns:
        salary_df_clean[salary_player_col] = salary_df_clean[salary_player_col].astype(str).str.strip()
    
    player_df_clean['Player'] = player_df_clean['Player'].astype(str).str.strip()
    
    # サラリー値の正規化
    salary_df_clean[salary_col] = pd.to_numeric(salary_df_clean[salary_col], errors='coerce')
    
    # 完全一致を試行
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
    
    # 完全一致が失敗した場合、ファジーマッチングを試行
    st.info("🔍 完全一致に失敗。ファジーマッチングを試行中...")
    
    merged_df = fuzzy_match_players(player_df_clean, salary_df_clean, salary_player_col, salary_col)
    
    if not merged_df.empty:
        return merged_df
    
    # ファジーマッチングも失敗した場合、名前の一部マッチングを試行
    st.info("🔍 ファジーマッチングに失敗。部分マッチングを試行中...")
    
    merged_df = partial_match_players(player_df_clean, salary_df_clean, salary_player_col, salary_col)
    
    return merged_df

def fuzzy_match_players(player_df, salary_df, salary_player_col, salary_col):
    """ファジーマッチング（類似度ベース）"""
    from difflib import SequenceMatcher
    
    matched_data = []
    stats_players = player_df['Player'].unique()
    salary_players = salary_df[salary_player_col].dropna().unique()
    
    for stats_name in stats_players:
        best_match = None
        best_score = 0
        
        for salary_name in salary_players:
            # 文字列の類似度を計算
            similarity = SequenceMatcher(None, 
                                       stats_name.lower().replace('.', ''), 
                                       str(salary_name).lower().replace('.', '')).ratio()
            
            if similarity > best_score and similarity >= 0.8:  # 80%以上の類似度
                best_score = similarity
                best_match = salary_name
        
        if best_match:
            # マッチした場合、データを追加
            player_stats = player_df[player_df['Player'] == stats_name].iloc[0]
            salary_info = salary_df[salary_df[salary_player_col] == best_match].iloc[0]
            
            matched_data.append({
                **player_stats.to_dict(),
                'Salary': salary_info[salary_col],
                'matched_salary_name': best_match,
                'match_score': best_score
            })
    
    if matched_data:
        merged_df = pd.DataFrame(matched_data)
        merged_df = merged_df[merged_df['Salary'].notna() & (merged_df['Salary'] > 0)]
        st.success(f"✅ ファジーマッチングで {len(merged_df)} プレイヤーをマッチング")
        return merged_df
    
    return pd.DataFrame()

def partial_match_players(player_df, salary_df, salary_player_col, salary_col):
    """部分マッチング（姓または名での一致）"""
    matched_data = []
    stats_players = player_df['Player'].unique()
    salary_players = salary_df[salary_player_col].dropna().unique()
    
    for stats_name in stats_players:
        # 名前を分割（姓と名）
        stats_parts = stats_name.split()
        
        for salary_name in salary_players:
            salary_parts = str(salary_name).split()
            
            # 姓または名が一致する場合
            if len(stats_parts) >= 2 and len(salary_parts) >= 2:
                if (stats_parts[-1].lower() == salary_parts[-1].lower() or  # 姓の一致
                    stats_parts[0].lower() == salary_parts[0].lower()):    # 名の一致
                    
                    # マッチした場合、データを追加
                    player_stats = player_df[player_df['Player'] == stats_name].iloc[0]
                    salary_info = salary_df[salary_df[salary_player_col] == salary_name].iloc[0]
                    
                    matched_data.append({
                        **player_stats.to_dict(),
                        'Salary': salary_info[salary_col],
                        'matched_salary_name': salary_name,
                        'match_type': 'partial'
                    })
                    break  # 最初のマッチで終了
    
    if matched_data:
        merged_df = pd.DataFrame(matched_data)
        merged_df = merged_df[merged_df['Salary'].notna() & (merged_df['Salary'] > 0)]
        st.success(f"✅ 部分マッチングで {len(merged_df)} プレイヤーをマッチング")
        return merged_df
    
    return pd.DataFrame()

def create_sample_salary_data(player_df):
    """サンプルサラリーデータの作成"""
    np.random.seed(42)
    players = player_df['Player'].unique()
    
    sample_salaries = []
    for player in players:
        player_stats = player_df[player_df['Player'] == player].iloc[0]
        
        # ベースサラリー
        base_salary = 2000000
        
        # パフォーマンスボーナス
        per_value = pd.to_numeric(player_stats.get('PER', 15), errors='coerce')
        per_value = per_value if not pd.isna(per_value) else 15
        per_bonus = per_value * 500000
        
        mp_value = pd.to_numeric(player_stats.get('MP', 20), errors='coerce')
        mp_value = mp_value if not pd.isna(mp_value) else 20
        mp_bonus = mp_value * 200000
        
        # スター選手ボーナス
        star_bonus = 0
        if any(name in str(player) for name in ['LeBron', 'Stephen', 'Giannis', 'Luka']):
            star_bonus = np.random.uniform(20000000, 30000000)
        elif any(name in str(player) for name in ['Kevin', 'Joel', 'Nikola', 'Jayson']):
            star_bonus = np.random.uniform(10000000, 20000000)
        
        # 最終サラリー
        salary = base_salary + per_bonus + mp_bonus + star_bonus + np.random.uniform(-2000000, 5000000)
        salary = max(salary, 1000000)  # 最低保証
        salary = min(salary, 60000000)  # 上限
        
        sample_salaries.append(int(salary))
    
    salary_df = pd.DataFrame({
        'Player': players,
        'current_salary': sample_salaries
    })
    
    merged_df = player_df.merge(salary_df, on='Player', how='inner')
    merged_df['Salary'] = merged_df['current_salary']
    st.success(f"✅ {len(merged_df)} プレイヤーのサンプルデータを作成しました")
    return merged_df

def apply_filters(merged_df):
    """フィルタリングの適用"""
    st.subheader("🔧 フィルタリングオプション")
    col1, col2 = st.columns(2)
    
    with col1:
        if 'MP' in merged_df.columns:
            min_minutes = st.slider("最低出場時間 (分/試合)", 5, 35, 15)
            merged_df['MP_numeric'] = pd.to_numeric(merged_df['MP'], errors='coerce').fillna(0)
            merged_df = merged_df[merged_df['MP_numeric'] >= min_minutes]
            st.write(f"出場時間フィルタ後: {len(merged_df)} プレイヤー")
    
    with col2:
        if len(merged_df) > 0:
            min_salary = int(merged_df['Salary'].min())
            max_salary = int(merged_df['Salary'].max())
            if min_salary < max_salary:
                salary_range = st.slider(
                    "サラリー範囲 (Million Dollar)",
                    min_value=min_salary//1000000,
                    max_value=max_salary//1000000,
                    value=(min_salary//1000000, max_salary//1000000)
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
    display_ranking_table(merged_df, selected_metric, efficiency_col, display_count)
    
    # 可視化
    if PLOTLY_AVAILABLE:
        create_visualizations(merged_df, selected_metric, efficiency_col)
    
    # サマリーとインサイト
    display_summary_and_insights(merged_df, selected_metric, efficiency_col)

def get_available_metrics(merged_df):
    """利用可能な効率指標を取得"""
    available_metrics = []
    for metric in ['PER', 'VORP', 'WS', 'BPM', 'TS%', 'USG%']:
        if metric in merged_df.columns:
            metric_values = pd.to_numeric(merged_df[metric], errors='coerce')
            if not metric_values.isna().all() and metric_values.sum() != 0:
                available_metrics.append(metric)
    return available_metrics

def display_ranking_table(merged_df, selected_metric, efficiency_col, display_count):
    """ランキングテーブルの表示"""
    top_players = merged_df.nlargest(display_count, efficiency_col)
    
    st.subheader(f"🏆 Top {display_count} プレイヤー効率ランキング")
    
    ranking_data = []
    for i, (_, player) in enumerate(top_players.iterrows(), 1):
        ranking_data.append({
            'Rank': i,
            'Player': player['Player'],
            'Team': player.get('Tm', 'N/A'),
            'Minutes': round(pd.to_numeric(player.get('MP', 0), errors='coerce'), 1),
            selected_metric: round(pd.to_numeric(player[selected_metric], errors='coerce'), 3),
            'Salary (M)': round(player['Salary'] / 1000000, 2),
            'Efficiency': round(player[efficiency_col], 8)
        })
    
    ranking_df = pd.DataFrame(ranking_data)
    
    st.dataframe(
        ranking_df.style
        .format({
            'Efficiency': '{:.8f}',
            'Salary (M)': '${:.2f}M',
            'Minutes': '{:.1f}'
        })
        .background_gradient(subset=['Efficiency'], cmap='RdYlGn')
        .highlight_max(subset=['Efficiency'], color='lightgreen'),
        use_container_width=True
    )

def create_visualizations(merged_df, selected_metric, efficiency_col):
    """可視化の作成"""
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
            color_continuous_scale='Viridis'
        )
        fig1.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        safe_plotly_chart(fig1)
    
    with col2:
        st.write("**効率 vs サラリー関係**")
        
        fig2 = px.scatter(
            merged_df,
            x='Salary',
            y=selected_metric,
            hover_data=['Player', 'Tm'] if 'Tm' in merged_df.columns else ['Player'],
            title=f'{selected_metric} vs Salary',
            labels={'Salary': 'Salary (Dollar)', selected_metric: selected_metric}
        )
        fig2.update_layout(height=500, xaxis_tickformat='$,.0f')
        safe_plotly_chart(fig2)

def display_summary_and_insights(merged_df, selected_metric, efficiency_col):
    """サマリーとインサイトの表示"""
    st.subheader("📈 サマリー統計")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("分析プレイヤー数", len(merged_df))
    
    with col2:
        avg_salary = merged_df['Salary'].mean()
        st.metric("平均サラリー", format_currency(avg_salary))
    
    with col3:
        avg_efficiency = merged_df[efficiency_col].mean()
        st.metric(f"平均{selected_metric}効率", f"{avg_efficiency:.6f}")
    
    with col4:
        best_player = merged_df.loc[merged_df[efficiency_col].idxmax(), 'Player']
        st.metric("最高効率プレイヤー", best_player)