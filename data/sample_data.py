import pandas as pd
import numpy as np
from config import NBA_TEAMS

def create_sample_data():
    """拡張サンプルデータ作成"""
    teams = list(NBA_TEAMS.keys())
    
    per_game_data = []
    advanced_team_data = []
    
    np.random.seed(42)
    for team in teams:
        # Per game stats - 正しいカラム名を使用
        per_game_data.append({
            'Team': team,
            'PTS': 110 + np.random.randint(-10, 15),
            'FG%': round(0.450 + np.random.uniform(-0.05, 0.05), 3),
            '3P%': round(0.350 + np.random.uniform(-0.05, 0.05), 3),
            'REB': 45 + np.random.randint(-5, 8),  # REBカラムを追加
            'AST': 25 + np.random.randint(-5, 8),
            'STL': 8 + np.random.randint(-2, 3),
            'BLK': 5 + np.random.randint(-2, 3),
            'TOV': 14 + np.random.randint(-3, 4)
        })
        
        # Advanced team stats
        ortg = 110 + np.random.randint(-8, 12)
        drtg = 110 + np.random.randint(-8, 12)
        advanced_team_data.append({
            'Team': team,
            'ORtg': ortg,
            'DRtg': drtg,
            'Pace': 100 + np.random.randint(-8, 8),
            'eFG%': round(0.520 + np.random.uniform(-0.04, 0.04), 3)
        })
    
    # プレイヤーデータ（より多くのプレイヤー）
    player_names = [
        'LeBron James', 'Stephen Curry', 'Giannis Antetokounmpo', 'Luka Doncic', 'Jayson Tatum',
        'Kevin Durant', 'Joel Embiid', 'Nikola Jokic', 'Damian Lillard', 'Jimmy Butler',
        'Kawhi Leonard', 'Paul George', 'Anthony Davis', 'Rudy Gobert', 'Draymond Green',
        'Klay Thompson', 'Russell Westbrook', 'Chris Paul', 'Kyrie Irving', 'James Harden',
        'Zion Williamson', 'Ja Morant', 'Trae Young', 'Devin Booker', 'Donovan Mitchell',
        'Bradley Beal', 'Karl-Anthony Towns', 'Ben Simmons', 'Pascal Siakam', 'CJ McCollum'
    ]
    
    advanced_data = []
    
    for i, player in enumerate(player_names):
        # より現実的な統計値の生成
        mp = round(25.0 + np.random.uniform(0, 15), 1)
        per = round(15.0 + np.random.uniform(0, 15), 2)
        ts_pct = round(0.500 + np.random.uniform(0, 0.150), 3)
        usg_pct = round(18.0 + np.random.uniform(0, 15), 1)
        
        advanced_data.append({
            'Player': player,
            'Tm': teams[i % len(teams)],
            'MP': mp,
            'PER': per,
            'TS%': ts_pct,
            'USG%': usg_pct,
            'VORP': round(np.random.uniform(-1.0, 8.0), 2),
            'WS': round(np.random.uniform(0, 15), 1),
            'BPM': round(np.random.uniform(-3.0, 10.0), 2)
        })
    
    # サラリーデータ（より現実的な分布）
    salary_data = []
    for player in player_names:
        # スター選手は高額、ベンチプレイヤーは低額
        if player in ['LeBron James', 'Stephen Curry', 'Giannis Antetokounmpo', 'Luka Doncic']:
            salary = np.random.uniform(40000000, 55000000)  # スーパースター
        elif player in ['Kevin Durant', 'Joel Embiid', 'Nikola Jokic', 'Jayson Tatum']:
            salary = np.random.uniform(30000000, 45000000)  # オールスター
        else:
            salary = np.random.uniform(5000000, 30000000)   # その他
        
        salary_data.append({
            'player_name': player,
            'current_salary': int(salary)
        })
    
    return {
        'per_game': pd.DataFrame(per_game_data),
        'advanced': pd.DataFrame(advanced_data + advanced_team_data),  # プレイヤーとチーム両方
        'play_by_play': pd.DataFrame(),
        'team_salaries': pd.DataFrame(),
        'player_salaries': pd.DataFrame(salary_data)
    }

def create_enhanced_player_data(num_players=100):
    """より多くのプレイヤーデータを生成"""
    np.random.seed(42)
    
    # 実際のNBA選手名の拡張リスト
    first_names = ['LeBron', 'Stephen', 'Giannis', 'Luka', 'Jayson', 'Kevin', 'Joel', 'Nikola', 
                   'Damian', 'Jimmy', 'Kawhi', 'Paul', 'Anthony', 'Rudy', 'Draymond',
                   'Klay', 'Russell', 'Chris', 'Kyrie', 'James', 'Zion', 'Ja', 'Trae',
                   'Devin', 'Donovan', 'Bradley', 'Karl-Anthony', 'Ben', 'Pascal', 'CJ']
    
    last_names = ['James', 'Curry', 'Antetokounmpo', 'Doncic', 'Tatum', 'Durant', 'Embiid',
                  'Jokic', 'Lillard', 'Butler', 'Leonard', 'George', 'Davis', 'Gobert',
                  'Green', 'Thompson', 'Westbrook', 'Paul', 'Irving', 'Harden', 'Williamson',
                  'Morant', 'Young', 'Booker', 'Mitchell', 'Beal', 'Towns', 'Simmons',
                  'Siakam', 'McCollum']
    
    teams = list(NBA_TEAMS.keys())
    players_data = []
    salary_data = []
    
    for i in range(num_players):
        first_name = np.random.choice(first_names)
        last_name = np.random.choice(last_names)
        player_name = f"{first_name} {last_name} {i+1}"  # 重複を避けるため番号を追加
        
        # プレイヤー統計
        mp = round(np.random.uniform(10, 40), 1)
        per = round(np.random.uniform(8, 30), 2)
        ts_pct = round(np.random.uniform(0.400, 0.700), 3)
        usg_pct = round(np.random.uniform(10, 35), 1)
        
        players_data.append({
            'Player': player_name,
            'Tm': np.random.choice(teams),
            'MP': mp,
            'PER': per,
            'TS%': ts_pct,
            'USG%': usg_pct,
            'VORP': round(np.random.uniform(-2.0, 10.0), 2),
            'WS': round(np.random.uniform(0, 20), 1),
            'BPM': round(np.random.uniform(-5.0, 12.0), 2)
        })
        
        # サラリー（出場時間と統計に基づく）
        base_salary = 2000000  # 最低サラリー
        performance_bonus = mp * per * 50000  # パフォーマンスボーナス
        salary = int(base_salary + performance_bonus + np.random.uniform(-1000000, 5000000))
        salary = max(salary, 1000000)  # 最低100万ドル
        salary = min(salary, 60000000)  # 最高6000万ドル
        
        salary_data.append({
            'player_name': player_name,
            'current_salary': salary
        })
    
    return pd.DataFrame(players_data), pd.DataFrame(salary_data)