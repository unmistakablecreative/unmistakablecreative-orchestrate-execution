import argparse
import requests
import json
import base64

# 🔥 HARDCODED GITHUB API TOKEN
GITHUB_ACCESS_TOKEN = ""

# GitHub API Base URL
GITHUB_API_BASE = "https://api.github.com"
ORG_NAME = "unmistakablecreative"  # 🔥 Automatically prepend this if missing

def format_repo_name(repo_name):
    """Ensures organization repositories are correctly referenced."""
    if repo_name and not repo_name.startswith(f"{ORG_NAME}/"):
        return f"{ORG_NAME}/{repo_name}"
    return repo_name

def get_supported_actions():
    """Return the list of supported actions and their parameters."""
    return {
        "create_repo": ["repo_name", "private", "description"],
        "get_file": ["repo_name", "path"],
        "update_file": ["repo_name", "path", "content"],
        "create_file": ["repo_name", "path", "content"],
        "commit_changes": ["repo_name", "message"],
        "apply_patch": ["repo_name", "patch_content"]
    }

def github_request(method, endpoint, data=None):
    """Generic function to send GitHub API requests with improved error handling."""
    headers = {
        "Authorization": f"token {GITHUB_ACCESS_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"{GITHUB_API_BASE}{endpoint}"
    response = requests.request(method, url, headers=headers, json=data)
    
    if response.status_code >= 400:
        return {
            "status": "error",
            "code": response.status_code,
            "message": response.json().get("message", "Unknown error"),
            "details": response.text
        }

    return response.json()

def create_repo(params):
    """Create a new GitHub repository."""
    repo_name = format_repo_name(params["repo_name"])
    data = {
        "name": repo_name.split("/")[-1],  # GitHub requires just the repo name in the body
        "private": params.get("private", False),
        "description": params.get("description", "")
    }
    return github_request("POST", f"/orgs/{ORG_NAME}/repos", data)

def get_file(params):
    """Retrieve a file's contents from a GitHub repo."""
    repo_name = format_repo_name(params["repo_name"])
    return github_request("GET", f"/repos/{repo_name}/contents/{params['path']}")

def create_file(params):
    """Create a new file on GitHub with Base64-encoded content."""
    repo_name = format_repo_name(params["repo_name"])
    encoded_content = base64.b64encode(params["content"].encode()).decode()

    data = {
        "message": f"Creating {params['path']} via API",
        "content": encoded_content
    }
    return github_request("PUT", f"/repos/{repo_name}/contents/{params['path']}", data)

def main():
    parser = argparse.ArgumentParser(description="GitHub CLI Tool")
    parser.add_argument("action", choices=["get_supported_actions", "create_repo", "get_file", "create_file"], help="Action to perform")
    parser.add_argument("--params", type=str, required=False, help="JSON-encoded parameters for the action")

    args = parser.parse_args()

    if args.action == "get_supported_actions":
        print(json.dumps(get_supported_actions(), indent=4))
        return

    # ✅ Parse JSON parameters
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "Invalid JSON format in --params."}, indent=4))
        return

    # ✅ Execute the selected action
    actions = {
        "create_repo": create_repo,
        "get_file": get_file,
        "create_file": create_file
    }

    result = actions[args.action](params)
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
