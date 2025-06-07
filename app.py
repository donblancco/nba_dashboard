#!/usr/bin/env python3
"""
NBA Analytics Dashboard - Streamlit App

Usage:
    streamlit run app.py
"""

import streamlit as st
import sys
import os

# プロジェクトのルートディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# メインアプリケーションのインポートと実行
try:
    from main import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    st.error(f"アプリケーションの読み込みに失敗しました: {e}")
    st.write("**トラブルシューティング:**")
    st.write("1. 必要なファイルが存在するか確認してください:")
    st.write("   - main.py")
    st.write("   - config.py") 
    st.write("   - data/loader.py")
    st.write("   - pages/ ディレクトリ")
    st.write("2. 必要なライブラリがインストールされているか確認してください:")
    st.code("pip install streamlit pandas numpy plotly", language="bash")
    
except Exception as e:
    st.error(f"予期しないエラーが発生しました: {e}")
    st.exception(e)