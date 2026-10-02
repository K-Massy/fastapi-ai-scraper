import requests
from bs4 import BeautifulSoup
import re
import logging # ① Python標準のロギングライブラリを導入

# IntelliJやDockerのログ画面で見やすいようにログの設定を行う
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def scrape_web_page(url: str) -> dict:
    try:
        # デバッグ開始の合図をログに出力
        logger.info(f"========== [スクレイピング開始] URL: {url} ==========")
        
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 【デバッグログ1】取得した生の全HTMLの文字数と、先頭のコードを出力
        logger.info(f"【DEBUG 1: 生HTML取得成功】 総文字数: {len(response.text)} 文字")
        logger.info(f"【生HTMLの先頭500文字】:\n{response.text[:500]}\n--------------------------------")

        soup = BeautifulSoup(response.text, "html.parser")

        # ① タイトルの取得
        title = soup.title.string if soup.title else "タイトル不明"
        title = re.sub(r'\s+', ' ', title).strip()
        logger.info(f"【DEBUG 2: 抽出タイトル】: {title}")

        # ② 【超確実ロジック】特定のクラス名に依存せず、ページ内の全テキストをバサッと取得
        # （不要なスクリプトやスタイルタグの中身は除外する）
        for script in soup(["script", "style", "meta", "noscript"]):
            script.decompose()

        # ページ全体の純粋な文字列だけを取り出す
        content_text = soup.get_text()

        # 行ごとの余計な空白を詰め、改行で繋ぎ直す
        lines = (line.strip() for line in content_text.splitlines())
        chunks = (phrase for line in lines for phrase in line.split("  "))
        clean_content = "\n".join(chunk for chunk in chunks if chunk)

        # AIのトークン節約のため、先頭から3000文字を切り出して渡す
        # （これだけあれば、ヘッダー等の雑音が入っても記事本編が必ず枠内に含まれます）
        final_content = clean_content[:3000] if clean_content else "本文が取得できませんでした。"

        # 【デバッグログ3】加工（パース）した後の、AIに引き渡す最終テキストを出力
        logger.info(f"【DEBUG 3: 加工後のテキスト（先頭500文字）】:\n{final_content[:500]}")
        logger.info("==================== [スクレイピング終了] ====================")

        return {
            "title": title,
            "content": final_content
        }

    except Exception as e:
        logger.error(f"【ERROR】スクレイピング中に例外が発生しました: {str(e)}")
        return {
            "title": "エラー",
            "content": f"スクレイピングに失敗しました: {str(e)}"
        }
