from fastapi import FastAPI
import os
import requests

app = FastAPI()

@app.get("/")
def read_root():
    """
    ルートエンドポイント: APIのステータス確認用
    """
    return {"message": "Welcome to FastAPI! The service is running."}

@app.post("/search_and_notify")
def search_and_notify(query: str):
    """
    GitHub検索を実行し、Slackに通知
    """
    # 環境変数の取得と検証
    github_token = os.getenv("GITHUB_TOKEN")
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    if not github_token:
        return {"error": "GITHUB_TOKEN 環境変数が設定されていません"}
    if not webhook_url:
        return {"error": "SLACK_WEBHOOK_URL 環境変数が設定されていません"}

    # GitHub APIの設定
    url = "https://api.github.com/search/code"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {"q": query}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code != 200:
            return {
                "error": f"GitHub APIエラー: {response.status_code}",
                "details": response.text
            }
    except requests.exceptions.RequestException as e:
        return {"error": "GitHub APIリクエストエラー", "details": str(e)}

    results = response.json().get("items", [])
    if not results:
        return {"message": "該当する結果はありません。"}

    # Slack通知
    message = f"検索クエリ 
query
 の結果 (上位5件):\n"
    for idx, result in enumerate(results[:5], 1):
        message += f"{idx}. ファイル名: {result[
name]}\n   URL: {result[html_url]}\n"

    try:
        slack_response = requests.post(webhook_url, json={"text": message}, timeout=10)
        if slack_response.status_code != 200:
            return {
                "error": "Slack通知エラー",
                "details": slack_response.text
            }
    except requests.exceptions.RequestException as e:
        return {"error": "Slack通知リクエストエラー", "details": str(e)}

    return {"message": "Slack通知が成功しました！"}
    
