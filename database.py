from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# ① 環境変数から接続情報を取得（Laravelの .env と同じ役割）
# docker-compose.ymlで指定した環境変数からURLを取得
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/fastapi_db")

# ② エンジンの作成（Laravelの内部的なPDO作成に相当）
# データベースエンジンを作成
engine = create_engine(DATABASE_URL)

# ③ セッションの工場（クラス）を作成
# データベースセッション（接続インスタンス）を作成するクラス
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ④ モデルの親玉クラス（Laravelの Illuminate\Database\Eloquent\Model に相当）
# モデルのベースクラス（LaravelのModelクラスのようなもの）
Base = declarative_base()

# ⑤ ★超重要：DBセッションを安全に管理する仕組み（依存性注入用）
# DBセッションを安全に生成・クローズするための関数（依存性注入用）
def get_db():
    db = SessionLocal() # DBに繋ぐ
    try:
        yield db        # コントローラー（関数）にDB接続を「一時的に貸し出す」
    finally:
        db.close()      # 処理が終わったら自動で絶対に接続を閉じる
