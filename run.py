from devbuddy.ai_generator import generate_code_change, generate_text
from devbuddy.GITManager import GITManagerGithub, clean_text, fix_escape_pattern
import json, os

BASE_BRANCH = 'main'


GITHUB_REPO, BASE_BRANCH, GITHUB_TOKEN, GITHUB_USER, LOCAL_REPO_PATH = (
    os.getenv("GITHUB_REPO"), 
    os.getenv("BASE_BRANCH"), 
    os.getenv("GITHUB_TOKEN"), 
    os.getenv("GITHUB_USER"),
    os.getenv("LOCAL_REPO_PATH")
)

manager = GITManagerGithub(repo_name=GITHUB_REPO, repo_token=GITHUB_TOKEN, repo_user=GITHUB_USER, local_path=LOCAL_REPO_PATH, ignore=['.git','package-lock.json','package.json','postcss.config.js'])
issues = manager.get_open_issues()


for issue in issues:
    manager.create_branch(BASE_BRANCH)
    print('brabnch created')
    issue_title = issue['title']
    issue_desc = issue['body']
    gen_changes = generate_code_change(issue_title, issue_desc, manager.repo_tree, manager.repo_content)
    changes = json.loads(fix_escape_pattern(gen_changes.replace('```json','').replace('```','')))
    branch_name = clean_text(issue_title).lower().replace(' ','_')
    manager.create_branch(branch_name)
    file_changes = [(f"{change['path']}/{change['filename']}",change['content']) for change in changes]
    manager.apply_code_changes(file_changes)
    commit_msg = generate_text(f"Create a commit message for the following code updates in 10 words. {str(changes)}")
    manager.commit_and_push(branch_name,commit_msg)