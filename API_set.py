from fastapi import FastAPI
import os
import requests

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI! The service is running."}

@app.post("/search_and_notify")
def search_and_notify(query: str):
    github_token = os.getenv("GITHUB_TOKEN")
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    if not github_token or not webhook_url:
        raise ValueError("Environment variables not set")

    url = "https://api.github.com/search/code"
    headers = {"Authorization": f"token {github_token}"}
    params = {"q": query}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return {"error": f"GitHub API error: {response.status_code}"}

    results = response.json().get("items", [])
    if not results:
        return {"message": "No results found."}

    message = "\n".join([f"{i+1}. {item['name']}: {item['html_url']}" for i, item in enumerate(results[:5])])

    slack_response = requests.post(webhook_url, json={"text": message})
    if slack_response.status_code != 200:
        return {"error": f"Slack notification error: {slack_response.status_code}"}

    return {"message": "Notification sent successfully!"}
