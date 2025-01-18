import os
from fastapi import FastAPI
import requests

app = FastAPI()

@app.post("/search_and_notify")
def search_and_notify(query: str):
    """
    GitHub検索を実行し、Slackに通知
    """
    # 環境変数からトークンとWebhook URLを取得
    github_token = os.getenv("GITHUB_TOKEN")
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    if not github_token or not webhook_url:
        raise ValueError("環境変数 GITHUB_TOKEN または SLACK_WEBHOOK_URL が設定されていません")

    # GitHub APIの設定
    url = "https://api.github.com/search/code"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {"q": query}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return {"error": f"GitHub APIエラー: {response.status_code}"}

    results = response.json().get("items", [])
    if not results:
        return {"message": "該当する結果はありません。"}

    # Slack通知
    message = f"検索クエリ '{query}' の結果:\n"
    for result in results[:5]:
        message += f"- ファイル名: {result['name']}\n  URL: {result['html_url']}\n\n"

    slack_response = requests.post(webhook_url, json={"text": message})
    if slack_response.status_code != 200:
        return {"error": "Slack通知エラー", "details": slack_response.text}

    return {"message": "Slack通知が成功しました！"}
