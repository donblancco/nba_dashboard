import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import os
from typing import Optional, List, Dict
import re

class NBAPlayerSalaryScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def clean_salary_text(self, salary_text: str) -> int:
        """サラリーテキストを数値に変換"""
        if not salary_text or salary_text in ['-', '--', 'N/A', '']:
            return 0
        
        # 記号と文字を除去
        cleaned = re.sub(r'[^\d]', '', salary_text)
        
        try:
            return int(cleaned) if cleaned else 0
        except ValueError:
            return 0
    
    def scrape_hoopshype(self) -> Optional[pd.DataFrame]:
        """HoopsHypeからサラリーデータを取得"""
        print("🏀 Scraping HoopsHype...")
        
        try:
            url = 'https://hoopshype.com/salaries/players/'
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            players = []
            
            # テーブル行を取得
            rows = soup.select('.hh-salaries-ranking-table tbody tr')
            if not rows:
                rows = soup.select('table tbody tr')
            
            print(f"Found {len(rows)} rows")
            
            for i, row in enumerate(rows):
                try:
                    cells = row.find_all('td')
                    if len(cells) < 3:
                        continue
                    
                    # プレイヤー名
                    name_element = cells[0].find('a') or cells[0]
                    name = name_element.get_text(strip=True)
                    
                    if not name or name.lower() in ['player', 'name']:
                        continue
                    
                    # チーム
                    team = cells[1].get_text(strip=True)
                    
                    # 現在のサラリー
                    current_salary = self.clean_salary_text(cells[2].get_text(strip=True))
                    
                    # 将来のサラリー
                    future_salaries = {}
                    for j, cell in enumerate(cells[3:8]):  # 最大5年分
                        salary_value = self.clean_salary_text(cell.get_text(strip=True))
                        if salary_value > 0:
                            future_salaries[f'salary_year_{j+2}'] = salary_value
                    
                    player_data = {
                        'player_name': name,
                        'team': team,
                        'current_salary': current_salary,
                        'rank': i + 1,
                        'source': 'hoopshype'
                    }
                    player_data.update(future_salaries)
                    
                    players.append(player_data)
                    
                    if (i + 1) % 50 == 0:
                        print(f"Processed {i + 1} players...")
                
                except Exception as e:
                    continue
            
            print(f"✅ HoopsHype: {len(players)} players extracted")
            return pd.DataFrame(players) if players else None
            
        except Exception as e:
            print(f"❌ HoopsHype error: {e}")
            return None
    
    def scrape_basketball_reference(self) -> Optional[pd.DataFrame]:
        """Basketball-Referenceからサラリーデータを取得"""
        print("🏀 Scraping Basketball-Reference...")
        
        try:
            url = 'https://www.basketball-reference.com/contracts/players.html'
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # pandasのread_htmlを使用
            tables = pd.read_html(response.text)
            
            for table in tables:
                if len(table) > 50 and any('salary' in str(col).lower() for col in table.columns):
                    df = table.copy()
                    
                    # カラム名をクリーンアップ
                    df.columns = [str(col).strip() for col in df.columns]
                    
                    # プレイヤー名とサラリーカラムを特定
                    player_col = None
                    salary_cols = []
                    
                    for col in df.columns:
                        if 'player' in str(col).lower():
                            player_col = col
                        elif any(year in str(col) for year in ['2024', '2025']) or 'salary' in str(col).lower():
                            salary_cols.append(col)
                    
                    if player_col and salary_cols:
                        players = []
                        for i, row in df.iterrows():
                            try:
                                name = str(row[player_col]).strip()
                                if not name or name == 'nan':
                                    continue
                                
                                current_salary = 0
                                if salary_cols:
                                    salary_text = str(row[salary_cols[0]])
                                    current_salary = self.clean_salary_text(salary_text)
                                
                                players.append({
                                    'player_name': name,
                                    'team': '',  # Basketball-Referenceはチーム情報が別
                                    'current_salary': current_salary,
                                    'rank': i + 1,
                                    'source': 'basketball_reference'
                                })
                            except:
                                continue
                        
                        print(f"✅ Basketball-Reference: {len(players)} players extracted")
                        return pd.DataFrame(players)
            
            return None
            
        except Exception as e:
            print(f"❌ Basketball-Reference error: {e}")
            return None
    
    def scrape_espn(self) -> Optional[pd.DataFrame]:
        """ESPNからサラリーデータを取得（簡易版）"""
        print("🏀 Attempting ESPN...")
        
        try:
            # ESPNは動的コンテンツが多いため、静的スクレイピングは困難
            # ここではデモ用の基本的な試行のみ
            url = 'https://www.espn.com/nba/salaries'
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # ESPNの構造は複雑なため、基本的な検出のみ
                tables = soup.find_all('table')
                if tables:
                    print("⚠️ ESPN: Found tables but requires more complex parsing")
            
            return None
            
        except Exception as e:
            print(f"❌ ESPN error: {e}")
            return None
    
    def process_traded_players(self, df: pd.DataFrame) -> pd.DataFrame:
        """移籍選手の処理：各選手について最新チームのみを保持"""
        if df.empty or 'player_name' not in df.columns or 'team' not in df.columns:
            return df
        
        print("🔄 Processing traded players...")
        
        # 各選手について重複をチェック
        processed_players = []
        player_groups = df.groupby('player_name')
        
        for player_name, group in player_groups:
            if len(group) == 1:
                # 重複なし：そのまま追加
                processed_players.append(group.iloc[0])
            else:
                # 重複あり：最新チームを決定
                print(f"   Found traded player: {player_name} ({len(group)} teams)")
                
                # TOTチームがある場合、TOT以外の最新チーム（最高サラリー）を選択
                non_tot_teams = group[group['team'] != 'TOT']
                if not non_tot_teams.empty:
                    # TOT以外で最高サラリーのレコード（最新契約）
                    latest_record = non_tot_teams.loc[non_tot_teams['current_salary'].idxmax()]
                    print(f"     → Selected current team: {latest_record['team']} (${latest_record['current_salary']:,})")
                else:
                    # TOTのみの場合はそれを使用
                    latest_record = group.iloc[0]
                    print(f"     → Only TOT available, keeping: {latest_record['team']}")
                
                processed_players.append(latest_record)
        
        # 新しいDataFrameを作成
        result_df = pd.DataFrame(processed_players)
        
        original_count = len(df)
        final_count = len(result_df)
        removed_count = original_count - final_count
        
        print(f"✅ Traded player processing complete:")
        print(f"   Original records: {original_count}")
        print(f"   Final records: {final_count}")
        print(f"   Removed duplicates: {removed_count}")
        
        return result_df

    def get_all_salaries(self) -> Optional[pd.DataFrame]:
        """複数のソースからサラリーデータを取得"""
        print("=== NBA Player Salary Collection Started ===\n")
        
        all_dataframes = []
        
        # 1. HoopsHype (メインソース)
        hoopshype_df = self.scrape_hoopshype()
        if hoopshype_df is not None:
            all_dataframes.append(hoopshype_df)
        
        time.sleep(2)  # レート制限対策
        
        # 2. Basketball-Reference (バックアップ)
        if not all_dataframes:  # HoopsHypeが失敗した場合のみ
            bref_df = self.scrape_basketball_reference()
            if bref_df is not None:
                all_dataframes.append(bref_df)
        
        time.sleep(2)
        
        # 3. ESPN (最後の手段)
        if not all_dataframes:
            espn_df = self.scrape_espn()
            if espn_df is not None:
                all_dataframes.append(espn_df)
        
        # データフレームを結合
        if all_dataframes:
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            
            # 移籍選手の処理（最新チームのみ保持）
            final_df = self.process_traded_players(combined_df)
            
            # ソート（サラリー順）
            final_df = final_df.sort_values('current_salary', ascending=False)
            final_df = final_df.reset_index(drop=True)
            final_df['final_rank'] = range(1, len(final_df) + 1)
            
            return final_df
        
        return None
    
    def save_to_json(self, df: pd.DataFrame, output_dir: str = 'nba_data') -> Dict[str, str]:
        """データをJSONファイルに保存"""
        os.makedirs(output_dir, exist_ok=True)
        
        files_created = {}
        
        # 1. 全プレイヤーサラリー
        player_file = os.path.join(output_dir, 'nba_player_salaries_2025.json')
        with open(player_file, 'w', encoding='utf-8') as f:
            json.dump(df.to_dict('records'), f, indent=2, ensure_ascii=False)
        files_created['players'] = player_file
        
        # 2. チーム別集計（チーム情報がある場合）
        if 'team' in df.columns and df['team'].notna().any():
            team_df = df.groupby('team').agg({
                'current_salary': ['sum', 'mean', 'count'],
                'player_name': 'count'
            }).round(0)
            
            team_df.columns = ['total_salary', 'avg_salary', 'salary_count', 'player_count']
            team_df = team_df.reset_index()
            team_df['salary_millions'] = (team_df['total_salary'] / 1000000).round(1)
            
            team_file = os.path.join(output_dir, 'nba_team_salaries_2025.json')
            with open(team_file, 'w', encoding='utf-8') as f:
                json.dump(team_df.to_dict('records'), f, indent=2, ensure_ascii=False)
            files_created['teams'] = team_file
        
        # 3. 統計サマリー
        stats = {
            'collection_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_players': len(df),
            'total_salary': int(df['current_salary'].sum()),
            'average_salary': int(df['current_salary'].mean()),
            'median_salary': int(df['current_salary'].median()),
            'max_salary': int(df['current_salary'].max()),
            'min_salary': int(df[df['current_salary'] > 0]['current_salary'].min()) if (df['current_salary'] > 0).any() else 0,
            'sources_used': df['source'].unique().tolist(),
            'top_10_players': df.head(10)[['player_name', 'team', 'current_salary']].to_dict('records')
        }
        
        stats_file = os.path.join(output_dir, 'nba_salary_stats_2025.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        files_created['stats'] = stats_file
        
        return files_created
    
    def run(self) -> None:
        """メイン実行関数"""
        print("🏀 NBA Player Salary Scraper")
        print("=" * 50)
        
        # データ取得
        salary_df = self.get_all_salaries()
        
        if salary_df is None or salary_df.empty:
            print("❌ Failed to collect salary data from any source")
            return
        
        # 統計表示
        print(f"\n📊 Collection Summary:")
        print(f"   Total Players: {len(salary_df):,}")
        print(f"   Total Payroll: ${salary_df['current_salary'].sum():,}")
        print(f"   Average Salary: ${salary_df['current_salary'].mean():,.0f}")
        print(f"   Highest Salary: ${salary_df['current_salary'].max():,}")
        
        # Top 10表示
        print(f"\n🏆 Top 10 Highest Paid Players:")
        top_10 = salary_df.head(10)
        for i, player in top_10.iterrows():
            team_info = f" ({player['team']})" if player['team'] else ""
            print(f"   {player['final_rank']:2d}. {player['player_name']}{team_info}: ${player['current_salary']:,}")
        
        # JSON保存
        print(f"\n💾 Saving to JSON files...")
        files_created = self.save_to_json(salary_df)
        
        print(f"\n✅ Files created:")
        for file_type, filepath in files_created.items():
            print(f"   {file_type}: {filepath}")
        
        print(f"\n🎉 NBA salary data collection completed successfully!")

def main():
    """スタンドアロン実行用"""
    scraper = NBAPlayerSalaryScraper()
    scraper.run()

if __name__ == "__main__":
    main()