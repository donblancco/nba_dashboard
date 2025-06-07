# App Runner最適化 Dockerfile
FROM python:3.9-slim

# メタデータ
LABEL maintainer="NBA Analytics Dashboard"
LABEL description="Streamlit-based NBA Analytics Dashboard for AWS App Runner"

# 作業ディレクトリ設定
WORKDIR /app

# システムの依存関係をインストール（キャッシュ効率化）
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係ファイルを先にコピー（Dockerキャッシュ最適化）
COPY requirements.txt .

# Pythonパッケージのインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY . .

# 非rootユーザーを作成（セキュリティ向上）
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# App Runner用のポート設定
EXPOSE 8080

# ヘルスチェック設定
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/_stcore/health || exit 1

# 環境変数設定
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# アプリケーション実行
CMD ["streamlit", "run", "app.py", \
     "--server.port=8080", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.runOnSave=false", \
     "--server.allowRunOnSave=false", \
     "--browser.gatherUsageStats=false"]