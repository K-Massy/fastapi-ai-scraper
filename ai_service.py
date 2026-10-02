import os
from openai import OpenAI

def summarize_text(text: str) -> str:
    # 環境変数からAPIキーを自動読み込みしてクライアントを初期化
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        # 最新の軽量・高速・低価格モデル「gpt-4o-mini」を使用
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは優秀なエンジニアです。入力された技術記事などの本文を、簡潔に3行の箇条書き（日本語）で要約してください。"
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.5, # 実行ごとのブレを少なくし、安定した要約にする設定
            max_tokens=300   # 出力文字数の上限
        )

        # AIから返ってきたテキストを取り出して返す
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"AI要約に失敗しました: {str(e)}"
