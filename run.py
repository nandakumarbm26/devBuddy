from devbuddy.ai_generator import generate_code_change, generate_text
from devbuddy.repo_handler import GitRepoManager,  clean_text, extract_json_objects, fix_escape_pattern
from devbuddy.github_utils import get_open_issues
import json

BASE_BRANCH = 'main'
issues = get_open_issues()


for issue in issues:
    manager = GitRepoManager("repo/nk", ignore=['.git','package-lock.json','package.json','postcss.config.js'])
    manager.create_branch(BASE_BRANCH)
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