
import requests

from dotenv import load_dotenv
import os
load_dotenv() 


GITHUB_TOKEN, GITHUB_REPO = os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_REPO")
if not GITHUB_TOKEN or not GITHUB_REPO:
    raise ValueError("Please set the GITHUB_TOKEN and GITHUB_REPO environment variables")

def get_open_issues():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return [issue for issue in response.json() if 'pull_request' not in issue]
