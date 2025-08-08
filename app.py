from flask import Flask, request
from dotenv import load_dotenv
import os
from devbuddy.ai import generate_code_change, generate_text
from devbuddy.GITManager import GITManagerGithub,  clean_text,  fix_escape_pattern
from devbuddy.github_utils import get_open_issues
import json
from devbuddy.logger import logging

BASE_BRANCH = 'main'
load_dotenv() 


LOG_FILE = os.getenv("LOG_FILE", "request_log.txt")

app = Flask(__name__)

@app.route('/print-body', methods=['POST'])
def print_body():
    data = request.get_data(as_text=True)  # Read raw body as text

    # Log to file
    with open(LOG_FILE, "a") as f:  # "a" means append mode
        f.write(f"New Request:\n{data}\n{'-'*40}\n")

    return "Body received and logged!", 200

@app.route('/issue_hook', methods=['POST'])
def issue_hook():
    data = request.get_json()
    if not data:
        logging.error("No JSON received.")
        return "Invalid or missing JSON.", 400

    if data.get('action') != 'opened':
        logging.info("Action is not 'opened'; ignoring.")
        return "Action ignored.", 200

    issue_title = data['issue'].get('title')
    issue_desc = data['issue'].get('body')

    logging.info(f"Received issue: {issue_title}")
    logging.info(f"Received issue description: {issue_desc}")

    if not issue_title or not issue_desc:
        logging.warning("Issue title or description is empty.")
        return "Issue title or description is empty.", 400

    try:
        manager = GITManagerGithub(
            "repo/nanda",
            ignore=['.git', 'package-lock.json', 'package.json', 'postcss.config.js']
        )
        logging.info("GITManagerGithub created successfully.")

        gen_changes = generate_code_change(issue_title, issue_desc, manager.repo_tree, manager.repo_content)
        logging.info("Code change generated.")

        fixed_changes = fix_escape_pattern(gen_changes.replace('```json', '').replace('```', ''))
        changes = json.loads(fixed_changes)
        logging.info("Code change JSON fixed and loaded.")

        branch_name = clean_text(issue_title).lower().replace(' ', '_')
        logging.info(f"Branch name created: {branch_name}")

        manager.create_branch(branch_name)
        logging.info("Branch created.")

        file_changes = [
            (f"{change['path']}/{change['filename']}", change['content'])
            for change in changes
        ]
        logging.info(f"File changes prepared: {file_changes}")

        manager.apply_code_changes(file_changes)
        logging.info("Code changes applied.")

        commit_msg = generate_text(f"Create a commit message for the following code updates in 10 words. {str(changes)}")
        logging.info(f"Commit message generated: {commit_msg}")

        manager.commit_and_push(branch_name, commit_msg)
        logging.info("Code changes committed and pushed.")

        return {
            "message": f"Branch '{branch_name}' created and changes pushed successfully."
        }, 200

    except Exception as e:
        logging.exception(f"Error occurred: {e}")
        return {
            "error": str(e)
        }, 500

if __name__ == '__main__':
    app.run(port=5000,debug=True)
