import streamlit as st
import pandas as pd
from utils.helpers import filter_multi_team_records

def create_page(data):
    """チーム概要ページ"""
    st.header("🏀 Team Overview")
    
    st.info("""
    **📊 チーム概要ページについて**
    
    このページでは、NBA全30チームの基本的な統計情報を確認できます：
    - 各チームの試合あたり平均スタッツ（得点、リバウンド、アシストなど）
    - チーム間の比較とランキング
    - データの詳細な検索・フィルタリング機能
    """)
    st.divider()
    
    if 'per_game' not in data or data['per_game'].empty:
        st.error("Per game データが見つかりません")
        return
    
    player_df = filter_multi_team_records(data['per_game'])
    
    # 選手データからチーム統計を集計
    if 'Team' not in player_df.columns:
        st.error("チーム情報が見つかりません")
        return
    
    # シンプルなアプローチ：TOTレコードを除外して重複選手は最新のチームを使用
    # NaN値をクリーンアップ
    clean_df = player_df.dropna(subset=['Player', 'Team']).copy()
    
    # TOTを除外
    non_tot_df = clean_df[clean_df['Team'] != 'TOT'].copy()
    
    # 各選手について最新のチーム（最大試合数）のレコードを保持
    if 'G' in non_tot_df.columns:
        # 試合数が最大のレコードを保持（最新チーム）
        current_team_players = non_tot_df.loc[non_tot_df.groupby('Player')['G'].idxmax()].copy()
    else:
        # 試合数がない場合は最後のレコードを保持
        current_team_players = non_tot_df.drop_duplicates(subset=['Player'], keep='last')
    
    # 実際に出場している選手のみをフィルタ
    if 'MP' in current_team_players.columns and 'G' in current_team_players.columns:
        active_players = current_team_players[
            (current_team_players['MP'].fillna(0) >= 10.0) |  # 平均出場時間10分以上
            (current_team_players['G'].fillna(0) >= 10)       # 10試合以上出場
        ].copy()
    else:
        active_players = current_team_players.copy()
    
    # チーム単位で統計を集計
    if len(active_players) == 0:
        st.error("処理対象の選手データがありません")
        return
    
    # 各選手の総統計値（1試合平均 × 試合数）を計算してからチーム合計
    if 'G' not in active_players.columns:
        st.error("試合数データ（G列）が見つかりません")
        return
    
    # 各選手の総統計値を計算
    stats_to_process = ['PTS', 'TRB', 'AST', 'STL', 'BLK', 'TOV']
    available_stats = [stat for stat in stats_to_process if stat in active_players.columns]
    
    if not available_stats:
        st.error("集計可能な統計データがありません")
        return
    
    # 各選手の総統計値を計算（1試合平均 × 試合数）
    enhanced_players = active_players.copy()
    for stat in available_stats:
        enhanced_players[f'{stat}_total'] = enhanced_players[stat] * enhanced_players['G']
    
    # チーム単位で集計
    agg_dict = {'G': 'max'}  # チーム内の最大試合数（シーズン全体の試合数に近い）
    for stat in available_stats:
        agg_dict[f'{stat}_total'] = 'sum'  # 総統計値の合計
    
    team_stats = enhanced_players.groupby('Team').agg(agg_dict).reset_index()
    
    # NaN値を0で埋める
    team_stats = team_stats.fillna(0)
    
    # NBAレギュラーシーズンの試合数（82試合）を使用
    NBA_REGULAR_SEASON_GAMES = 82
    
    # チームの1試合平均を計算（総統計値 ÷ 82試合）
    for stat in available_stats:
        if f'{stat}_total' in team_stats.columns:
            team_stats[f'{stat}_per_game'] = team_stats[f'{stat}_total'] / NBA_REGULAR_SEASON_GAMES
    
    # デバッグ情報（必要に応じて表示）
    if st.checkbox("🔍 デバッグ情報を表示"):
        st.write("**元の選手データサンプル:**")
        st.dataframe(player_df[['Player', 'Team', 'PTS', 'G']].head(10))
        
        st.write("**重複除去後の選手データサンプル:**")
        st.dataframe(current_team_players[['Player', 'Team', 'PTS', 'G']].head(10))
        
        st.write("**チーム統計データ:**")
        st.write(f"チーム数: {len(team_stats)}")
        if len(team_stats) > 0:
            st.write("**サンプルチームデータ:**")
            st.dataframe(team_stats.head(3))
            
        st.write("**1つのチームの詳細確認:**")
        if len(team_stats) > 0:
            sample_team = team_stats.iloc[0]['Team']
            all_team_players = player_df[player_df['Team'] == sample_team][['Player', 'PTS', 'G', 'MP']] if 'MP' in player_df.columns else player_df[player_df['Team'] == sample_team][['Player', 'PTS', 'G']]
            active_team_players = active_players[active_players['Team'] == sample_team][['Player', 'PTS', 'G', 'MP']] if 'MP' in active_players.columns else active_players[active_players['Team'] == sample_team][['Player', 'PTS', 'G']]
            
            st.write(f"チーム: {sample_team}")
            st.write(f"全選手数: {len(all_team_players)}, アクティブ選手数: {len(active_team_players)}")
            st.write("**アクティブ選手のみ:**")
            
            # 計算詳細を表示
            if not active_team_players.empty:
                debug_df = active_team_players.copy()
                debug_df['総得点'] = debug_df['PTS'] * debug_df['G']
                st.dataframe(debug_df)
                
                total_points = debug_df['総得点'].sum()
                team_games = 82  # NBAレギュラーシーズン試合数
                calculated_avg = total_points / team_games
                
                st.write(f"**計算詳細:**")
                st.write(f"- 選手総得点の合計: {total_points:,.0f}")
                st.write(f"- チーム試合数: {team_games}")
                st.write(f"- 計算されたチーム平均: {calculated_avg:.1f} 点/試合")
                st.write(f"- team_statsでの値: {team_stats[team_stats['Team'] == sample_team]['PTS_per_game'].iloc[0]:.1f}")
            else:
                st.write("アクティブ選手データなし")
    
    # メトリクス表示用のカラム
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'PTS_per_game' in team_stats.columns and len(team_stats) > 0:
            avg_team_pts = team_stats['PTS_per_game'].mean()
            max_pts_team = team_stats.loc[team_stats['PTS_per_game'].idxmax(), 'Team']
            st.metric(
                label="平均チーム得点",
                value=f"{avg_team_pts:.1f}",
                delta=f"最高: {max_pts_team}"
            )
        else:
            st.metric(
                label="平均チーム得点", 
                value="N/A",
                help="PTSカラムが見つかりません"
            )
    
    with col2:
        if 'TRB_per_game' in team_stats.columns and len(team_stats) > 0:
            avg_team_reb = team_stats['TRB_per_game'].mean()
            max_reb_team = team_stats.loc[team_stats['TRB_per_game'].idxmax(), 'Team']
            st.metric(
                label="平均チームリバウンド",
                value=f"{avg_team_reb:.1f}",
                delta=f"最高: {max_reb_team}"
            )
        else:
            st.metric(
                label="平均チームリバウンド",
                value="N/A"
            )
    
    with col3:
        if 'AST_per_game' in team_stats.columns and len(team_stats) > 0:
            avg_team_ast = team_stats['AST_per_game'].mean()
            max_ast_team = team_stats.loc[team_stats['AST_per_game'].idxmax(), 'Team']
            st.metric(
                label="平均チームアシスト",
                value=f"{avg_team_ast:.1f}",
                delta=f"最高: {max_ast_team}"
            )
        else:
            st.metric(
                label="平均チームアシスト",
                value="N/A"
            )
    
    with col4:
        if 'STL_per_game' in team_stats.columns and len(team_stats) > 0:
            avg_team_stl = team_stats['STL_per_game'].mean()
            max_stl_team = team_stats.loc[team_stats['STL_per_game'].idxmax(), 'Team']
            st.metric(
                label="平均チームスティール",
                value=f"{avg_team_stl:.1f}",
                delta=f"最高: {max_stl_team}"
            )
        else:
            st.metric(
                label="平均チームスティール",
                value="N/A"
            )
    
    # チーム統計ランキング表示
    st.subheader("📋 チーム統計ランキング")
    
    if len(team_stats) > 0:
        # 表示する列を準備
        display_columns = ['Team', 'PTS_per_game', 'TRB_per_game', 'AST_per_game', 'STL_per_game', 'BLK_per_game', 'TOV_per_game']
        available_columns = [col for col in display_columns if col in team_stats.columns]
        
        if available_columns:
            # 列名を日本語に変更
            display_df = team_stats[available_columns].copy()
            column_mapping = {
                'Team': 'チーム',
                'PTS_per_game': '得点/試合',
                'TRB_per_game': 'リバウンド/試合',
                'AST_per_game': 'アシスト/試合', 
                'STL_per_game': 'スティール/試合',
                'BLK_per_game': 'ブロック/試合',
                'TOV_per_game': 'ターンオーバー/試合'
            }
            display_df = display_df.rename(columns=column_mapping)
            
            # 得点順でソート
            if '得点/試合' in display_df.columns:
                display_df = display_df.sort_values('得点/試合', ascending=False)
            
            # 数値は小数点1桁で表示
            numeric_cols = display_df.select_dtypes(include=['float64', 'int64']).columns
            for col in numeric_cols:
                display_df[col] = display_df[col].round(1)
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("表示可能なチーム統計データがありません")
    else:
        st.info("チーム統計データが見つかりません")