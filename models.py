from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base # ① database.pyで作成した「親玉クラス」をインポート

# ② Laravelの「Model」にあたるクラスを定義
class Article(Base):
    __tablename__ = "articles" # ③ 実際のデータベースのテーブル名を指定

    # ④ 各カラム（列）の定義
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    url = Column(String(2048), nullable=False)
    summary = Column(Text, nullable=True) # AIが生成する要約テキスト

    # ⑤ 作成日時の自動記録（Laravelの timestamps の一部に相当）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
