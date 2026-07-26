# scripts/devops_github.py
import os
import sys
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.abspath("./test_project/gourmetgo-platform")

def log(msg):
    print(f"[DevOps & GitHub Integrator] {msg}")

def init_git_repo(project_dir=PROJECT_ROOT):
    """Initializes a local git repository and creates an initial commit."""
    if not os.path.exists(project_dir):
        log(f"⚠️ Directory {project_dir} does not exist yet. Run main_v2.py first.")
        return False

    log(f"Initializing Git repository at: {project_dir}")

    # 1. Write standard .gitignore
    gitignore_path = os.path.join(project_dir, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write("node_modules/\n.env\ndist/\nbuild/\n*.log\n.venv/\n__pycache__/\n")
        log("Created .gitignore file.")

    # 2. Run git init
    subprocess.run(["git", "init"], cwd=project_dir, check=True)
    subprocess.run(["git", "add", "."], cwd=project_dir, check=True)

    # 3. Check if there are commits
    res = subprocess.run(["git", "status", "--porcelain"], cwd=project_dir, capture_output=True, text=True)
    if res.stdout.strip():
        subprocess.run(["git", "commit", "-m", "feat: Initial release by AI Software Engineering Organization"], cwd=project_dir, check=True)
        log("✅ Local Git commit created successfully!")
    else:
        log("Git repository is up to date (no uncommitted changes).")

    return True

def publish_to_github(repo_name="gourmetgo-platform", is_private=True, project_dir=PROJECT_ROOT):
    """Creates a remote GitHub repository using GITHUB_TOKEN and pushes local main branch."""
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        log("⚠️ GITHUB_TOKEN not found in .env file! Skipping GitHub remote repository creation.")
        log("To enable auto-publishing to GitHub, add GITHUB_TOKEN=ghp_xxx to your .env file.")
        return False

    log(f"Connecting to GitHub API to create repository: '{repo_name}'...")
    
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }
    payload = {
        "name": repo_name,
        "description": "Generated platform built by AI Software Engineering Organization",
        "private": is_private,
        "auto_init": False
    }

    response = requests.post("https://api.github.com/user/repos", headers=headers, json=payload)
    
    if response.status_code == 201:
        repo_data = response.json()
        clone_url = repo_data.get("clone_url")
        html_url = repo_data.get("html_url")
        log(f"🎉 Created GitHub repository successfully: {html_url}")

        # Set remote and push
        subprocess.run(["git", "branch", "-M", "main"], cwd=project_dir)
        subprocess.run(["git", "remote", "add", "origin", clone_url], cwd=project_dir)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=project_dir)
        log(f"✅ Code pushed to GitHub: {html_url}")
        return html_url
    elif response.status_code == 422:
        log(f"Repository '{repo_name}' already exists on your GitHub account.")
    else:
        log(f"GitHub API Error ({response.status_code}): {response.text}")
    return False

def main():
    log("="*60)
    log("  DEVOPS & GITHUB AUTOMATED DEPLOYMENT TOOL  ")
    log("="*60)

    if init_git_repo():
        publish_to_github()

if __name__ == "__main__":
    main()
