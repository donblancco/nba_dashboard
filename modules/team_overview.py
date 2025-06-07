import streamlit as st
import pandas as pd

def create_page(data):
    """チーム概要ページ"""
    st.header("🏀 Team Overview")
    
    if 'per_game' not in data or data['per_game'].empty:
        st.error("Per game データが見つかりません")
        return
    
    df = data['per_game']
    
    # デバッグ情報（必要に応じて表示）
    if st.checkbox("🔍 デバッグ情報を表示"):
        st.write("**利用可能なカラム:**")
        st.write(list(df.columns))
        st.write("**データ形状:**")
        st.write(f"行数: {len(df)}, 列数: {len(df.columns)}")
        if len(df) > 0:
            st.write("**サンプルデータ:**")
            st.dataframe(df.head(3))
    
    # メトリクス表示用のカラム
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'PTS' in df.columns:
            avg_pts = df['PTS'].mean()
            max_pts_team = df.loc[df['PTS'].idxmax(), 'Team'] if 'Team' in df.columns else "N/A"
            st.metric(
                label="平均得点",
                value=f"{avg_pts:.1f}",
                delta=f"最高: {max_pts_team}"
            )
        else:
            st.metric(
                label="平均得点", 
                value="N/A",
                help="PTSカラムが見つかりません"
            )
    
    with col2:
        if 'FG%' in df.columns:
            avg_fg = df['FG%'].mean()
            st.metric(
                label="平均FG%",
                value=f"{avg_fg:.3f}"
            )
        else:
            st.metric(
                label="平均FG%", 
                value="N/A",
                help="FG%カラムが見つかりません"
            )
    
    with col3:
        if 'AST' in df.columns:
            avg_ast = df['AST'].mean()
            st.metric(
                label="平均アシスト",
                value=f"{avg_ast:.1f}"
            )
        else:
            st.metric(
                label="平均アシスト", 
                value="N/A",
                help="ASTカラムが見つかりません"
            )
    
    with col4:
        if 'REB' in df.columns:
            avg_reb = df['REB'].mean()
            st.metric(
                label="平均リバウンド",
                value=f"{avg_reb:.1f}"
            )
        else:
            st.metric(
                label="平均リバウンド", 
                value="N/A",
                help="REBカラムが見つかりません"
            )
    
    # 追加の統計情報
    st.subheader("📊 追加統計")
    
    # 利用可能な統計の動的表示
    additional_stats = []
    stat_mappings = {
        '3P%': '3ポイント成功率',
        'STL': 'スティール',
        'BLK': 'ブロック',
        'TOV': 'ターンオーバー'
    }
    
    for stat, description in stat_mappings.items():
        if stat in df.columns:
            additional_stats.append((stat, description, df[stat].mean()))
    
    if additional_stats:
        # 追加統計を2列で表示
        cols = st.columns(2)
        for i, (stat, desc, avg_val) in enumerate(additional_stats):
            with cols[i % 2]:
                st.metric(
                    label=f"平均{desc}",
                    value=f"{avg_val:.3f}" if stat.endswith('%') else f"{avg_val:.1f}"
                )
    
    # データテーブル
    st.subheader("📊 チームデータ")
    
    # 表示する列を選択（存在する列のみ）
    display_columns = ['Team']
    for col in ['PTS', 'FG%', '3P%', 'REB', 'AST', 'STL', 'BLK', 'TOV']:
        if col in df.columns:
            display_columns.append(col)
    
    # データの表示
    if len(display_columns) > 1:  # Team以外にも表示する列がある場合
        display_df = df[display_columns].copy()
        
        # ソートオプション
        if len(display_columns) > 2:  # 2列以上ある場合にソート機能を提供
            sort_col = st.selectbox(
                "ソートする列を選択:",
                options=['なし'] + [col for col in display_columns if col != 'Team'],
                index=0
            )
            
            if sort_col != 'なし':
                sort_ascending = st.checkbox("昇順でソート", value=False)
                display_df = display_df.sort_values(sort_col, ascending=sort_ascending)
        
        st.dataframe(display_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)
    
    # 統計サマリー
    st.subheader("📈 統計サマリー")
    
    # 数値カラムのみで統計サマリーを作成
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    if numeric_cols:
        summary_df = df[numeric_cols].describe()
        st.dataframe(summary_df, use_container_width=True)
        
        # 基本情報
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("チーム数", len(df))
        
        with col2:
            st.metric("統計項目数", len(numeric_cols))
        
        with col3:
            null_count = df.isnull().sum().sum()
            st.metric("欠損値", null_count)
    else:
        st.warning("数値データが見つからないため、統計サマリーを表示できません")
    
    # データ品質レポート
    with st.expander("📋 データ品質レポート"):
        st.write("**カラムの存在確認:**")
        expected_columns = ['Team', 'PTS', 'FG%', 'AST', 'REB', '3P%', 'STL', 'BLK', 'TOV']
        
        for col in expected_columns:
            if col in df.columns:
                st.success(f"✅ {col}: 存在")
            else:
                st.error(f"❌ {col}: 不存在")
        
        st.write("**データ型情報:**")
        dtype_info = df.dtypes.to_dict()
        for col, dtype in dtype_info.items():
            st.write(f"- {col}: {dtype}")
        
        st.write("**欠損値情報:**")
        null_info = df.isnull().sum()
        for col in null_info.index:
            null_count = null_info[col]
            if null_count > 0:
                st.warning(f"⚠️ {col}: {null_count} 個の欠損値")
            else:
                st.info(f"✅ {col}: 欠損値なし")