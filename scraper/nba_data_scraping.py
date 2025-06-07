import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def scrape_basketball_reference_table(url, output_filename):
    """
    Basketball Referenceのページからテーブルを取得してJSONとして保存
    
    Args:
        url (str): スクレイピング対象のURL
        output_filename (str): 出力ファイル名
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Fetching data from: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # HTMLをパース
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # メインの統計テーブルを探す（通常はid="stats"）
        table = soup.find('table', {'id': 'stats'})
        
        if not table:
            # 他の可能なテーブルIDも試す
            possible_ids = ['per_game-team', 'advanced-team', 'play-by-play-team', 'totals-team']
            for table_id in possible_ids:
                table = soup.find('table', {'id': table_id})
                if table:
                    break
        
        if not table:
            # クラス名でも探してみる
            table = soup.find('table', class_='stats_table')
        
        if not table:
            print(f"Warning: No table found for {url}")
            return None
        
        # pandasでテーブルを読み取り
        df = pd.read_html(str(table))[0]
        
        # マルチレベルカラムの処理
        if isinstance(df.columns, pd.MultiIndex):
            # マルチレベルカラムを結合
            df.columns = [' '.join(col).strip() if col[1] != '' else col[0] for col in df.columns.values]
        
        # 不要な行を削除（ヘッダーが重複している行など）
        df = df[df.iloc[:, 0] != df.columns[0]]  # ヘッダー行の重複を削除
        
        # 空の行を削除
        df = df.dropna(how='all')
        
        # インデックスをリセット
        df = df.reset_index(drop=True)
        
        # JSONに変換
        json_data = df.to_json(orient='records', indent=2)
        
        # ファイルに保存
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(json_data)
        
        print(f"Successfully saved {len(df)} records to {output_filename}")
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None

def main():
    """メイン処理"""
    
    # スクレイピング対象のURL
    urls = [
        {
            'url': 'https://www.basketball-reference.com/leagues/NBA_2025_advanced.html',
            'filename': 'nba_2025_advanced_stats.json'
        },
        {
            'url': 'https://www.basketball-reference.com/leagues/NBA_2025_per_game.html', 
            'filename': 'nba_2025_per_game_stats.json'
        },
        {
            'url': 'https://www.basketball-reference.com/leagues/NBA_2025_play-by-play.html',
            'filename': 'nba_2025_play_by_play_stats.json'
        }
    ]
    
    # 出力ディレクトリの作成
    output_dir = 'nba_data'
    os.makedirs(output_dir, exist_ok=True)
    
    results = {}
    
    for url_info in urls:
        url = url_info['url']
        filename = os.path.join(output_dir, url_info['filename'])
        
        # データを取得
        df = scrape_basketball_reference_table(url, filename)
        
        if df is not None:
            results[url_info['filename']] = {
                'records': len(df),
                'columns': list(df.columns)
            }
        
        # リクエスト間隔を空ける（サーバーに負荷をかけないため）
        time.sleep(2)
    
    # 結果サマリーを出力
    print("\n=== Scraping Results ===")
    for filename, info in results.items():
        print(f"{filename}: {info['records']} records, {len(info['columns'])} columns")
        print(f"  Columns: {', '.join(info['columns'][:5])}..." if len(info['columns']) > 5 else f"  Columns: {', '.join(info['columns'])}")
        print()

if __name__ == "__main__":
    main()
