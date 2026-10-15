from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
from database import engine, get_db
from pydantic import BaseModel
import scraper
import ai_service
import logging # ① Python標準のロギングライブラリを導入
from fastapi.responses import StreamingResponse
import pandas as pd
import io

# IntelliJやDockerのログ画面で見やすいようにログの設定を行う
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class ArticleCreate(BaseModel):
    url: str

class ArticleResponse(BaseModel):
    id: int
    title: str
    url: str
    summary: str | None

    class Config:
        from_attributes = True

# 記事を登録するAPI（POST）
@app.post("/articles", response_model=ArticleResponse)
def create_article(article: ArticleCreate, db: Session = Depends(get_db)):
    # デバッグ開始の合図をログに出力
    logger.info(f"========== [スクレイピング開始] URL: {article} ==========")

    scraped_data = scraper.scrape_web_page(article.url)

    # 【デバッグログ1】取得した生の全HTMLの文字数と、先頭のコードを出力
    debug_content = scraped_data['content']
    logger.info(f"【DEBUG 1: スクレイピング後の文字】 総文字数: {len(debug_content)} 文字")
    logger.info(f"【先頭500文字】:\n{debug_content[:500]}\n--------------------------------")

    if scraped_data["title"] == "エラー":
        raise HTTPException(status_code=400, detail=scraped_data["content"])

    ai_summary = ai_service.summarize_text(scraped_data["content"])

    # 【デバッグログ3】AIが指定通りに生成テキストを出力
    logger.info(f"【DEBUG 3: 生成後のテキスト（先頭500文字）】:\n{ai_summary[:500]}")
    logger.info("==================== [スクレイピング終了] ====================")

    db_article = models.Article(
        title=scraped_data["title"],
        url=article.url,
        summary=ai_summary
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

# 記事一覧を取得するAPI（GET）
@app.get("/articles", response_model=List[ArticleResponse])
def read_articles(db: Session = Depends(get_db)):
    return db.query(models.Article).all()

# 3. 登録された記事データをExcelファイルとしてダウンロードするAPI（GET）
@app.get("/articles/download/excel")
def download_articles_excel(db: Session = Depends(get_db)):
    # ① データベースからすべての記事を取得（Laravelの Article::all() に相当）
    articles = db.query(models.Article).all()

    if not articles:
        raise HTTPException(status_code=404, detail="ダウンロードするデータがありません。")

    # ② データベースのオブジェクト配列を、Pythonの辞書（連想配列）のリストに変換
    data = []
    for a in articles:
        data.append({
            "ID": a.id,
            "タイトル": a.title,
            "URL": a.url,
            "AI要約文": a.summary,
            "登録日時": a.created_at.strftime("%Y-%m-%d %H:%M:%S") if a.created_at else ""
        })

    # ③ pandasを使ってデータフレーム（表データ構造）を作成
    df = pd.DataFrame(data)

    # ④ メモリ上にバイナリストリーム（仮想ファイル）を用意
    output = io.BytesIO()

    # ⑤ Excelライターを使ってメモリ上のファイルに書き込み
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="記事一覧")

    # ⑥ ファイルの読み込み位置を先頭に戻す
    output.seek(0)

    # ⑦ ファイル名を設定（日本語が文字化けしないように設定）
    headers = {
        'Content-Disposition': 'attachment; filename="articles_list.xlsx"'
    }

    # ⑧ ブラウザに向けてExcelファイルをストリーム配信
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )
