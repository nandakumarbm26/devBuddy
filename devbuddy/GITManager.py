import os, requests
from pathlib import Path
from git import Repo, GitCommandError
import re
import json
from devbuddy.logger import logging
from dotenv import load_dotenv
import os
from abc import ABC, abstractmethod

load_dotenv() 
LOG_FILE = os.getenv("LOG_FILE", "request_log.txt")

GITHUB_REPO, BASE_BRANCH, GITHUB_TOKEN, GITHUB_USER = (os.getenv("GITHUB_REPO"), os.getenv("BASE_BRANCH"), os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_USER")
)
if not GITHUB_REPO or not BASE_BRANCH or not GITHUB_TOKEN or not GITHUB_USER:
    raise ValueError("Please set the GITHUB_REPO, BASE_BRANCH, GITHUB_TOKEN, and GITHUB_USER environment variables")




LOG_FILE = os.getenv("LOG_FILE", "request_log.txt")



class GitRepoManagerBase(ABC):
    def __init__(self, repo_name:str, repo_token:str, repo_user:str, local_path: str = None, ignore=[".git"]):

        self._local_path = local_path if local_path else f"repo/{repo_name}"
        self._ignore = ignore
        self._repo_name = repo_name
        self.repo_token = repo_token
        self.repo_user = repo_user

        self.repo = self.clone_or_get_repo()
        self.repo_tree = self.get_folder_structure()
        self.repo_content = self.build_tree_with_file_contents()
        
        pass

    @abstractmethod
    def clone_or_get_repo(self) -> Repo:
        pass

    @abstractmethod
    def get_open_issues(self):
        pass

    @abstractmethod
    def repo_exists(self) -> bool:
        pass

    def apply_code_changes(self, changes: list[tuple[str, str]]):
        for filename, content in changes:
            file_path = os.path.join(self._local_path, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

    def commit_and_push(self, branch_name: str, commit_message: str):
        self.create_branch(branch_name)
        self.repo.git.add('--all')
        self.repo.index.commit(commit_message)
        self.repo.git.push('--set-upstream', 'origin', branch_name)
        logging.info(f"Commited : branch,{branch_name}, Commit,{commit_message}")

    def create_branch(self, branch_name: str, checkout: bool = True):
        try:
            branch_names = [str(br) for br in self.repo.branches]
            if branch_name in branch_names:
                logging.info(f"Branch '{branch_name}' already exists locally.")
                if checkout:
                    br = self.repo.branches[branch_names.index(branch_name)]
                    br.checkout()
                    logging.info(f"Checked out existing branch '{branch_name}'.")
                    return br
            else:
                br = self.repo.create_head(branch_name)
                if checkout:
                    br.checkout()
                    return br
        except GitCommandError as e:
            logging.error(f"Error creating or checking out branch '{branch_name}': {e}")
            raise RuntimeError(f"Git command failed: {e}")

    def get_folder_structure(self) -> str:
        if self._ignore is None:
            self._ignore = []
        response = ""
        for root, dirs, files in os.walk(self._local_path):
            level = root.replace(self._local_path, '').count(os.sep)
            indent = ' ' * 4 * level
            folder_name = os.path.basename(root)
            if folder_name in self._ignore:
                dirs[:] = []
                continue
            response += f"{indent}{folder_name}/\n"
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                response += f"{subindent}{f}\n"
            dirs[:] = [d for d in dirs if d not in self._ignore]
        return response

    def build_tree_with_file_contents(self) -> dict:
        if self._ignore is None:
            self._ignore = [".git"]
        return self._build_tree_recursive(Path(self._local_path))

    def _build_tree_recursive(self, path: Path) -> dict:
        tree = {}
        for item in path.iterdir():
            if item.name in self._ignore or item.suffix in ['.svg', '.png', '.jpeg', '.css']:
                continue
            if item.is_dir():
                tree[item.name] = self._build_tree_recursive(item)
            else:
                try:
                    content = item.read_text(encoding='utf-8')
                except Exception as e:
                    content = f"<Error reading file: {e}>"
                tree[item.name] = content
        return tree



class GITManagerGithub(GitRepoManagerBase):
    def __init__(self, repo_name: str, repo_token: str, repo_user: str, local_path: str = None, ignore=[".git"]):
        if not repo_user or not BASE_BRANCH or not GITHUB_TOKEN or not GITHUB_USER:
            raise ValueError("Please set the GITHUB_REPO, BASE_BRANCH, GITHUB_TOKEN, and GITHUB_USER environment variables")

        self._repo_url = f"https://{repo_user}:{repo_token}@github.com/{repo_name}.git"
        super().__init__(repo_name, repo_token, repo_user, local_path, ignore)
        # self.repo_exists()

        print(self._repo_url)
        pass
    
    def repo_exists(self) -> bool:
        url = f"https://api.github.com/repos/{self._repo_user}/{self.repo}"
        headers = {
            "Authorization": f"token {self.repo_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
       
        return True
        
    def clone_or_get_repo(self) -> Repo:        
        if os.path.exists(self._local_path):
            return Repo(self._local_path)
        return Repo.clone_from(self._repo_url, self._local_path)

    def get_open_issues(self):
        url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"GitHub API error: {response.status_code} - {response.text}")
            return []


class GITManagerDevops(GitRepoManagerBase):
    def clone_or_get_repo(self) -> Repo:
        org = os.getenv("DEVOPS_ORG")
        project = os.getenv("DEVOPS_PROJECT")
        repo = os.getenv("DEVOPS_REPO")
        token = os.getenv("DEVOPS_PAT")

        if not org or not project or not repo or not token:
            raise ValueError("Missing DevOps credentials in environment variables")

        repo_url = f"https://{token}@dev.azure.com/{org}/{project}/_git/{repo}"
        if os.path.exists(self._local_path):
            return Repo(self._local_path)
        return Repo.clone_from(repo_url, self._local_path)

    def get_open_issues(self):
        org = os.getenv("DEVOPS_ORG")
        project = os.getenv("DEVOPS_PROJECT")
        token = os.getenv("DEVOPS_PAT")
        url = f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems?api-version=6.0"
        headers = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Azure DevOps API error: {response.status_code} - {response.text}")
            return []




def clean_text(s):
    return re.sub(r'[^a-zA-Z0-9]', '', s)

def fix_escape_pattern(s):
    return re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', s)
    
def extract_json_objects(text):
    """
    Extract all JSON objects from a string using regex.

    Args:
        text (str): The input text containing JSON objects.

    Returns:
        list: A list of parsed Python dictionaries.
    """
    # This regex matches JSON-like object strings (handles nested braces)
    json_pattern = re.compile(r'\{(?:[^{}]|(?R))*\}')
    
    matches = json_pattern.findall(text)
    json_objects = []
    
    for match in matches:
        try:
            parsed = json.loads(match)
            json_objects.append(parsed)
        except json.JSONDecodeError:
            continue  # Skip invalid JSON blocks

    return json_objects
