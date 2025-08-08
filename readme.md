# GITManager Module

This module provides classes and utilities for managing Git repositories and interacting with GitHub and Azure DevOps, including issue retrieval, repository cloning, and file structure introspection.

## Features

- **GitRepoManagerBase**: Abstract base class for repository management, supporting:
  - Cloning or accessing local repositories
  - Applying code changes and committing/pushing to branches
  - Building file tree structures and reading file contents
- **GITManagerGithub**: GitHub-specific implementation for:
  - Cloning repositories from GitHub
  - Fetching open issues via the GitHub API
- **GITManagerDevops**: Azure DevOps-specific implementation for:
  - Cloning repositories from Azure DevOps
  - Fetching open work items via the Azure DevOps API
- **Utility Functions**:
  - `clean_text(s)`: Removes non-alphanumeric characters from a string
  - `fix_escape_pattern(s)`: Escapes invalid backslashes in strings
  - `extract_json_objects(text)`: Extracts all JSON objects from a string using regex

## Environment Variables

Set the following variables in your `.env` file or environment:

- For GitHub:
  - `GITHUB_REPO`, `BASE_BRANCH`, `GITHUB_TOKEN`, `GITHUB_USER`
- For Azure DevOps:
  - `DEVOPS_ORG`, `DEVOPS_PROJECT`, `DEVOPS_REPO`, `DEVOPS_PAT`
- Optional:
  - `LOG_FILE` (default: `request_log.txt`)

## Example Usage

```python
from devbuddy.GITManager import GITManagerGithub, GITManagerDevops

# For GitHub
github_manager = GITManagerGithub()
issues = github_manager.get_open_issues()

# For Azure DevOps
devops_manager = GITManagerDevops()
work_items = devops_manager.get_open_issues()
```

---

# AI Generator Module

This module provides integration with Azure OpenAI (OpenAI) to automate code generation and text completion tasks for developer workflows.

## Features

- **OpenAI Class**: Wrapper for Azure OpenAI API, supporting chat completions and embeddings.
- **generate_text(prompt)**: Generates concise text responses using the AI model.
- **generate_code_change(issue_title, issue_body, files_tree, file_content)**: Produces code change suggestions in JSON format based on a GitHub issue and the current codebase context.

## Environment Variables

Ensure the following variables are set (see `.env`):

- `NEXSUS_API_ENDPOINT`: Azure OpenAI endpoint URL.
- `NEXSUS_API_KEY`: API key for authentication.
- `NEXSUS_DEPLOYMENT_NAME`: Model deployment name.

## Usage Example

```python
from devbuddy.ai_generator import generate_code_change, generate_text

# Generate a commit message
commit_msg = generate_text("Summarize the following code changes...")

# Generate code changes for an issue
changes_json = generate_code_change(
    issue_title="Fix bug in login flow",
    issue_body="Login fails when username contains special characters.",
    files_tree="project structure here",
    file_content="file contents here"
)
```

---

## 🔧 Required Environment Variables

Before running the application, ensure the following environment variables are set:

| Variable Name            | Description                                                                  |
| ------------------------ | ---------------------------------------------------------------------------- |
| `GITHUB_TOKEN`           | Personal access token with access to the GitHub repository.                  |
| `GITHUB_REPO`            | Full name of the GitHub repository (e.g., `username/repo`).                  |
| `BASE_BRANCH`            | The base branch to which changes will be merged (e.g., `main` or `develop`). |
| `NEXSUS_API_KEY`         | API key to authenticate with the Nexsus API.                                 |
| `NEXSUS_API_ENDPOINT`    | The endpoint URL of the Nexsus API.                                          |
| `NEXSUS_DEPLOYMENT_NAME` | Name of the deployment to be triggered or managed on Nexsus.                 |
| `GITHUB_USER`            | GitHub username of the account performing actions.                           |
| `LOG_FILE`               | Path or name of the log file to store application logs.                      |

Set these variables in your `.env` file or in your deployment environment.

---

```

```
