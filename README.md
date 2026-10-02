# FastAPI × OpenAI API 技術記事自動要約システム (MVP)

URLを入力するだけで、対象ページのHTMLをスクレイピングし、OpenAIのLLMを活用して自動で「日本語3行の箇条書き」に要約してデータベースに保存するWebシステムです。
長期案件の端境期におけるモダン技術（Python/AI/モダンインフラ）のキャッチアップの一環として構築しました。

## 🛠️ 技術スタック
- **Backend:** Python 3.11 / FastAPI
- **OR Mapper:** SQLAlchemy (Data Mapper方式)
- **Database:** PostgreSQL 11
- **AI Integration:** OpenAI API (`gpt-4o-mini`)
- **Scraping:** BeautifulSoup4 / requests
- **Infrastructure:** Docker / Docker Compose
- **IDE:** IntelliJ IDEA Ultimate (Docker Interpreter連携)

## ✨ 主な機能・特徴
1. **堅牢な汎用スクレイピングロジック**
   - 特定のフロントエンド構造（CSSクラス名等）に依存せず、不要なタグ（script/style等）を除外してページ全体の純粋なテキストを抽出。サイトの仕様変更に強い設計。
2. **LLM（OpenAI）を活用した3行要約**
   - 抽出したテキストを `gpt-4o-mini` に投入し、エンジニア向けに最適化された日本語3行の箇条書き要約を自動生成。
3. **ロギングによるデバッグ追跡**
   - 標準ロギングライブラリ（`logging`）を組み込み、生HTMLの取得状況からパース後のテキストまで、Dockerログ上で処理プロセスを完全追跡可能。

## 🚀 起動方法
1. ルートディレクトリに `.env` ファイルを作成し、OpenAIのAPIキーを設定。
2. コンテナの起動：
   ```bash
   docker compose up -d --build
   ```
3. ブラウザで `http://localhost:8000/docs` (Swagger UI) を開き、APIテストを実行可能。
