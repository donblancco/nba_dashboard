# NBA Analytics Dashboard

2024-25シーズンのNBAデータを分析・可視化するStreamlitベースのダッシュボードアプリケーションです。

## 機能

このアプリケーションは以下の7つの分析モジュールを提供します：

1. **チーム概要** - チーム統計のサマリー表示
2. **スコアリング分析** - 得点力とシュート効率の分析
3. **チーム比較** - 複数チームの統計比較
4. **高度な分析** - 高度なNBA指標の分析
5. **サラリー効率** - チーム/選手の給与対パフォーマンス分析
6. **相関分析** - 各指標間の統計的相関
7. **データエクスプローラー** - カスタムデータ探索

## 必要な環境

- Python 3.9以上
- 必要なライブラリは`requirements.txt`に記載

## インストール方法

```bash
# リポジトリのクローン
git clone <repository-url>
cd nba_dashboard

# 仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt


```

## 使い方

### ローカルでの実行

```bash
# 最初にデータを収集（必須）
python scraper/nba_data_scraping.py
python scraper/nba_salary_scraper.py

# Streamlitアプリの起動
streamlit run main.py

# または、App Runner対応版で起動
streamlit run app.py
```

ブラウザが自動的に開き、`http://localhost:8501`でアプリケーションにアクセスできます。

### 基本的な操作

1. **ページ選択**: 左側のサイドバーから分析したいモジュールを選択
2. **データの確認**: 各ページで表示されるデータテーブルや可視化を確認
3. **インタラクティブ操作**:
   - グラフはマウスオーバーで詳細情報表示
   - データテーブルはソート可能
   - チーム比較では複数チームを選択可能

### 各モジュールの使い方

#### チーム概要
- 全チームの基本統計を一覧表示
- 平均得点、FG%、アシスト、リバウンドなどを確認

#### スコアリング分析
- 得点上位15チームのランキング
- シュート効率（FG% vs 3P%）の散布図で分析

#### チーム比較
- 複数チームを選択して統計を並べて比較
- レーダーチャートで視覚的に比較

#### サラリー効率
- チーム総年俸と成績の関係を分析
- コストパフォーマンスの良いチーム/選手を発見

## データの更新

データは`nba_data/`ディレクトリ内のJSONファイルから読み込まれます：

```bash
# スクレイパーを使用してデータを更新
python scraper/nba_data_scraping.py
python scraper/nba_salary_scraper.py
```

## Docker での実行

```bash
# イメージのビルド
docker build -t nba-dashboard .

# コンテナの実行
docker run -p 8080:8080 nba-dashboard
```

## AWS App Runner へのデプロイ

1. `apprunner.yaml`の設定を確認
2. AWS CLIでデプロイ：
```bash
aws apprunner create-service --cli-input-yaml file://apprunner.yaml
```

## データ形式

アプリケーションは以下のデータファイルを使用：

- `nba_2025_per_game_stats.json` - チームのゲーム平均統計
- `nba_2025_advanced_stats.json` - 高度な統計指標
- `nba_2025_play_by_play_stats.json` - プレイバイプレイ統計
- `nba_player_salaries_2025.json` - 選手の年俸データ
- `nba_team_salaries_2025.json` - チーム総年俸データ

## トラブルシューティング

### データが表示されない場合
- 最初にスクレイパーを実行してデータを収集してください：
  ```bash
  python scraper/nba_data_scraping.py
  python scraper/nba_salary_scraper.py
  ```
- `nba_data/`ディレクトリにJSONファイルが存在することを確認
- サンプルデータモードで動作している可能性があります

### スクレイパーが動作しない場合
- 必要なライブラリがインストールされているか確認：
- インターネット接続を確認
- Basketball ReferenceやHoopsHypeのサイトがアクセス可能か確認

### ポートエラーの場合
```bash
# 別のポートで起動
streamlit run main.py --server.port 8502
```

### メモリ不足の場合
- `config.py`でデータキャッシュの設定を調整
- より小さいデータセットを使用

## 開発者向け情報

### プロジェクト構造
```
nba_dashboard/
├── app.py              # App Runner用エントリーポイント
├── main.py             # ローカル開発用エントリーポイント
├── config.py           # アプリケーション設定
├── requirements.txt    # Python依存関係
├── modules/            # 分析モジュール
├── data/              # データローダー
├── utils/             # ユーティリティ関数
├── nba_data/          # NBAデータ（JSON）
└── scraper/           # データスクレイピングツール
```

### カスタマイズ
- 新しい分析モジュールは`modules/`に追加
- データ処理は`data/loader.py`を修正
- UIスタイルは`config.py`のCSS設定を調整

