import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from config import PLOTLY_AVAILABLE, safe_plotly_chart, format_currency

def create_page(data):
    """サラリー効率分析ページ"""
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
    
    # サラリーデータの処理
    merged_df = process_salary_data(data, player_df)
    
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

def process_salary_data(data, player_df):
    """サラリーデータの処理とマージ"""
    use_real_salary = False
    
    if 'player_salaries' in data and not data['player_salaries'].empty:
        salary_df = data['player_salaries'].copy()
        st.info(f"💰 {len(salary_df)} プレイヤーのサラリーデータを確認中...")
        
        # サラリーデータの構造を分析
        merged_df = attempt_real_salary_merge(player_df, salary_df)
        
        if not merged_df.empty:
            return merged_df
    
    # サンプルデータを使用
    st.info("🧪 サンプルサラリーデータを作成中...")
    return create_sample_salary_data(player_df)

def attempt_real_salary_merge(player_df, salary_df):
    """実際のサラリーデータとのマージを試行"""
    # プレイヤー名カラムを特定
    salary_player_col = None
    for col in ['player_name', 'Player', 'name']:
        if col in salary_df.columns:
            salary_player_col = col
            break
    
    # サラリーカラムを特定
    salary_col = None
    for col in ['current_salary', 'salary', 'total_salary', '2024-25']:
        if col in salary_df.columns:
            salary_col = col
            break
    
    if not salary_player_col or not salary_col:
        st.warning(f"❌ サラリーデータの構造が不明: {list(salary_df.columns)}")
        return pd.DataFrame()
    
    st.write(f"✅ サラリーデータ構造: プレイヤー名='{salary_player_col}', サラリー='{salary_col}'")
    
    # データクリーニング
    salary_df[salary_player_col] = salary_df[salary_player_col].astype(str).str.strip()
    player_df['Player'] = player_df['Player'].astype(str).str.strip()
    
    # デバッグ情報表示オプション
    show_debug = st.checkbox("🔍 マージデバッグ情報を表示")
    
    if show_debug:
        show_merge_debug_info(player_df, salary_df, salary_player_col)
    
    # マージ試行
    merged_df = player_df.merge(
        salary_df[[salary_player_col, salary_col]], 
        left_on='Player', 
        right_on=salary_player_col, 
        how='inner'
    )
    
    if not merged_df.empty:
        merged_df['Salary'] = pd.to_numeric(merged_df[salary_col], errors='coerce').fillna(0)
        merged_df = merged_df[merged_df['Salary'] > 0]
        st.success(f"✅ {len(merged_df)} プレイヤーのサラリーデータをマージしました")
        return merged_df
    else:
        st.warning("❌ 実際のサラリーデータのマージに失敗。サンプルデータを使用します。")
        return pd.DataFrame()

def show_merge_debug_info(player_df, salary_df, salary_player_col):
    """マージ失敗時のデバッグ情報表示"""
    with st.expander("🔍 マージ失敗の詳細分析"):
        stats_players = set(player_df['Player'].unique())
        salary_players = set(salary_df[salary_player_col].unique())
        
        st.write(f"**統計データプレイヤー数**: {len(stats_players)}")
        st.write(f"**サラリーデータプレイヤー数**: {len(salary_players)}")
        
        # 完全一致
        common_players = stats_players.intersection(salary_players)
        st.write(f"**完全一致プレイヤー数**: {len(common_players)}")
        if common_players:
            st.write(f"**一致例**: {list(common_players)[:5]}")
        
        # 部分一致分析
        partial_matches = find_partial_matches(stats_players, salary_players)
        if partial_matches:
            st.write("**部分一致の可能性**:")
            for match in partial_matches[:10]:
                st.write(f"  - {match[0]} ↔ {match[1]} (類似度: {match[2]:.2f})")
        
        # サンプル表示
        col1, col2 = st.columns(2)
        with col1:
            st.write("**統計データのプレイヤー例**:")
            st.write(list(stats_players)[:10])
        with col2:
            st.write("**サラリーデータのプレイヤー例**:")
            st.write(list(salary_players)[:10])

def find_partial_matches(stats_players, salary_players, threshold=0.8):
    """部分一致するプレイヤー名を検索"""
    from difflib import SequenceMatcher
    
    matches = []
    for stats_name in list(stats_players)[:20]:  # 処理時間を考慮して制限
        for salary_name in salary_players:
            similarity = SequenceMatcher(None, stats_name.lower(), salary_name.lower()).ratio()
            if similarity >= threshold:
                matches.append((stats_name, salary_name, similarity))
    
    return sorted(matches, key=lambda x: x[2], reverse=True)

def create_sample_salary_data(player_df):
    """サンプルサラリーデータの作成"""
    np.random.seed(42)
    players = player_df['Player'].unique()
    
    sample_salaries = []
    for player in players:
        # プレイヤーの統計に基づいてサラリーを生成
        player_stats = player_df[player_df['Player'] == player].iloc[0]
        
        # ベースサラリー
        base_salary = 2000000
        
        # パフォーマンスボーナス
        per_bonus = player_stats.get('PER', 15) * 500000
        mp_bonus = player_stats.get('MP', 20) * 200000
        
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
    merged_df = merged_df[merged_df[efficiency_col] > 0]  # 負の効率値を除外
    
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
    
    # 美しいテーブル表示
    st.dataframe(
        ranking_df.style
        .format({
            'Efficiency': '{:.8f}',
            'Salary (M)': '${:.2f}M',
            'Minutes': '{:.1f}'
        })
        .background_gradient(subset=['Efficiency'], cmap='RdYlGn')
        .highlight_max(subset=['Efficiency'], color='lightgreen')
        .set_properties(**{
            'text-align': 'center',
            'font-size': '12px'
        }),
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
            color_continuous_scale='Viridis',
            text=efficiency_col
        )
        fig1.update_layout(
            height=500, 
            yaxis={'categoryorder':'total ascending'},
            xaxis_title=f'{selected_metric} per Million Dollar',
            yaxis_title='Player'
        )
        fig1.update_traces(texttemplate='%{text:.6f}', textposition='outside')
        safe_plotly_chart(fig1)
    
    with col2:
        st.write("**効率 vs サラリー関係**")
        
        # Top 10をハイライト
        top_10_names = set(merged_df.nlargest(10, efficiency_col)['Player'])
        merged_df['is_top10'] = merged_df['Player'].isin(top_10_names)
        
        fig2 = px.scatter(
            merged_df,
            x='Salary',
            y=selected_metric,
            hover_data=['Player', 'Tm'] if 'Tm' in merged_df.columns else ['Player'],
            title=f'{selected_metric} vs Salary',
            labels={
                'Salary': 'Salary (Dollar)',
                selected_metric: selected_metric
            },
            color='is_top10',
            color_discrete_map={True: 'red', False: 'blue'},
            size='MP' if 'MP' in merged_df.columns else None,
            size_max=15
        )
        
        fig2.update_layout(
            height=500,
            xaxis_tickformat='$,.0f',
            showlegend=True
        )
        safe_plotly_chart(fig2)
    
    # 追加の可視化
    create_additional_charts(merged_df, selected_metric, efficiency_col)

def create_additional_charts(merged_df, selected_metric, efficiency_col):
    """追加のチャート作成"""
    if not PLOTLY_AVAILABLE:
        return
    
    st.subheader("📈 詳細分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 効率分布
        st.write("**効率分布**")
        fig3 = px.histogram(
            merged_df,
            x=efficiency_col,
            title=f'{selected_metric} Efficiency Distribution',
            labels={efficiency_col: f'{selected_metric} Efficiency'},
            nbins=20
        )
        
        avg_efficiency = merged_df[efficiency_col].mean()
        fig3.add_vline(
            x=avg_efficiency,
            line_dash="dash",
            line_color="red",
            annotation_text=f"平均: {avg_efficiency:.6f}"
        )
        
        fig3.update_layout(height=400)
        safe_plotly_chart(fig3)
    
    with col2:
        # チーム別効率
        if 'Tm' in merged_df.columns:
            st.write("**チーム別平均効率**")
            team_efficiency = merged_df.groupby('Tm')[efficiency_col].mean().reset_index()
            team_efficiency = team_efficiency.sort_values(efficiency_col, ascending=False).head(10)
            
            fig4 = px.bar(
                team_efficiency,
                x='Tm',
                y=efficiency_col,
                title=f'Top 10 Teams - Average {selected_metric} Efficiency',
                labels={efficiency_col: f'Average {selected_metric} Efficiency'}
            )
            
            fig4.update_layout(height=400)
            safe_plotly_chart(fig4)

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
    
    # インサイト
    st.subheader("💡 注目ポイント")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # バリュー契約プレイヤー
        value_threshold = merged_df['Salary'].quantile(0.3)
        value_players = merged_df[merged_df['Salary'] <= value_threshold]
        
        if not value_players.empty:
            best_value = value_players.loc[value_players[efficiency_col].idxmax()]
            st.success(
                f"🌟 **バリュー契約MVP**: {best_value['Player']}\n\n"
                f"サラリー: {format_currency(best_value['Salary'])} | "
                f"効率: {best_value[efficiency_col]:.6f}"
            )
    
    with col2:
        # 高額契約の効率プレイヤー
        expensive_threshold = merged_df['Salary'].quantile(0.8)
        expensive_players = merged_df[merged_df['Salary'] >= expensive_threshold]
        
        if not expensive_players.empty:
            best_expensive = expensive_players.loc[expensive_players[efficiency_col].idxmax()]
            st.info(
                f"💰 **高額契約で最も効率的**: {best_expensive['Player']}\n\n"
                f"サラリー: {format_currency(best_expensive['Salary'])} | "
                f"効率: {best_expensive[efficiency_col]:.6f}"
            )
    
    # 追加統計
    display_additional_insights(merged_df, selected_metric, efficiency_col)

def display_additional_insights(merged_df, selected_metric, efficiency_col):
    """追加のインサイト表示"""
    st.subheader("🔍 追加分析")
    
    # 効率の四分位数分析
    q1 = merged_df[efficiency_col].quantile(0.25)
    q2 = merged_df[efficiency_col].quantile(0.50)
    q3 = merged_df[efficiency_col].quantile(0.75)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("効率 25%点", f"{q1:.6f}")
    
    with col2:
        st.metric("効率 中央値", f"{q2:.6f}")
    
    with col3:
        st.metric("効率 75%点", f"{q3:.6f}")
    
    # ポジション別分析（チーム情報がある場合）
    if 'Tm' in merged_df.columns:
        st.write("**チーム別統計**")
        team_stats = merged_df.groupby('Tm').agg({
            efficiency_col: ['mean', 'max', 'count'],
            'Salary': 'mean'
        }).round(6)
        
        team_stats.columns = ['平均効率', '最高効率', 'プレイヤー数', '平均サラリー']
        team_stats['平均サラリー'] = team_stats['平均サラリー'].apply(lambda x: f"${x/1000000:.1f}M")
        
        st.dataframe(team_stats.head(10), use_container_width=True)
    
    # データ品質情報
    st.info(f"💡 分析対象: {len(merged_df)} プレイヤー | 効率指標: {selected_metric} | データの信頼性: {'実データ' if '実際' in str(st.session_state) else 'サンプルデータ'}")
