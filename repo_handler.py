import os
from pathlib import Path
from git import Repo, GitCommandError
import re
import json
from logger import logging
from dotenv import load_dotenv
import os
load_dotenv() 


LOG_FILE = os.getenv("LOG_FILE", "request_log.txt")
GITHUB_REPO, BASE_BRANCH, GITHUB_TOKEN, GITHUB_USER = os.getenv("GITHUB_REPO"), os.getenv("BASE_BRANCH"), os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_USER")
if not GITHUB_REPO or not BASE_BRANCH or not GITHUB_TOKEN or not GITHUB_USER:
    raise ValueError("Please set the GITHUB_REPO, BASE_BRANCH, GITHUB_TOKEN, and GITHUB_USER environment variables")

class GitRepoManager:
    def __init__(self, local_path: str, ignore=[".git"]):
        self.local_path = local_path
        self.ignore = ignore
        self.repo = self.clone_or_get_repo()
        self.repo_tree = self.get_folder_structure()
        self.repo_content = self.build_tree_with_file_contents()

    def clone_or_get_repo(self) -> Repo:
        repo_url = f"https://{GITHUB_USER}:{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
        if os.path.exists(self.local_path):
            return Repo(self.local_path)
        return Repo.clone_from(repo_url, self.local_path)

    def apply_code_changes(self, changes: list[tuple[str, str]]):
        for filename, content in changes:
            file_path = os.path.join(self.local_path, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

    def commit_and_push(self, branch_name: str, commit_message: str):
        self.create_branch(branch_name)
        self.repo.git.add('--all')
        self.repo.index.commit(commit_message)
        self.repo.git.push('--set-upstream', 'origin', branch_name)
        logging.info("Commited : branch",branch_name, "Commit",commit_message)

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
        if self.ignore is None:
           self.ignore = []
        response = ""
        for root, dirs, files in os.walk(self.local_path):
            level = root.replace(self.local_path, '').count(os.sep)
            indent = ' ' * 4 * level
            folder_name = os.path.basename(root)
            if folder_name in self.ignore:
                dirs[:] = []
                continue
            response += f"{indent}{folder_name}/\n"
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                response += f"{subindent}{f}\n"
            dirs[:] = [d for d in dirs if d not in self.ignore]
        return response

    def build_tree_with_file_contents(self) -> dict:
        if self.ignore is None:
           self.ignore = [".git"]
        return self._build_tree_recursive(Path(self.local_path))

    def _build_tree_recursive(self, path: Path) -> dict:
        tree = {}
        for item in path.iterdir():
            if item.name in self.ignore or item.suffix in ['.svg', '.png', '.jpeg', '.css']:
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
