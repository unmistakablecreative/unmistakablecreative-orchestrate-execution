import argparse
import json
import os
import requests

# 🔥 HARD-CODED DROPBOX CREDENTIALS TO ENSURE FASTAPI SEES THEM


# Dropbox API Endpoints
DROPBOX_API_URL = "https://api.dropboxapi.com/2"
DROPBOX_CONTENT_URL = "https://content.dropboxapi.com/2"
DROPBOX_OAUTH_URL = "https://api.dropbox.com/oauth2/token"

def get_supported_actions():
    """Returns the list of supported actions and required parameters."""
    return {
        "search_files": ["query"],
        "download_file": ["path"],
        "generate_temporary_link": ["path"],
        "move_file": ["source_path", "destination_path"]
    }

def refresh_dropbox_token():
    """Refreshes the Dropbox access token dynamically."""
    response = requests.post(DROPBOX_OAUTH_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": DROPBOX_REFRESH_TOKEN
    }, auth=(DROPBOX_APP_KEY, DROPBOX_APP_SECRET))

    if response.status_code == 200:
        new_token = response.json().get("access_token")
        global DROPBOX_ACCESS_TOKEN
        DROPBOX_ACCESS_TOKEN = new_token  # Update in memory
        return new_token
    else:
        raise ValueError(f"❌ Failed to refresh Dropbox token: {response.text}")

def get_access_token():
    """Ensures we always have a valid access token."""
    return DROPBOX_ACCESS_TOKEN

def make_request(endpoint, method="POST", headers=None, json_payload=None, content_download=False):
    """Helper function to make API requests."""
    url = f"{DROPBOX_API_URL}/{endpoint}" if not content_download else f"{DROPBOX_CONTENT_URL}/{endpoint}"
    headers = headers or {}
    headers["Authorization"] = f"Bearer {get_access_token()}"
    headers["Content-Type"] = "application/json"

    response = requests.post(url, headers=headers, json=json_payload) if method == "POST" else requests.get(url, headers=headers)
    
    if response.status_code == 401:  # Token expired, refresh and retry
        headers["Authorization"] = f"Bearer {refresh_dropbox_token()}"
        response = requests.post(url, headers=headers, json=json_payload) if method == "POST" else requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json() if not content_download else response.content
    return {"status": "error", "message": response.text}

def search_files(query):
    """Search for files matching the query."""
    payload = {"query": query}
    return make_request("files/search_v2", json_payload=payload)

def download_file(path):
    """Download a file from Dropbox."""
    headers = {"Dropbox-API-Arg": json.dumps({"path": path})}
    return make_request("files/download", headers=headers, content_download=True)

def generate_temporary_link(path):
    """Generate a temporary download link."""
    result = make_request("files/get_temporary_link", json_payload={"path": path})
    return {"status": "success", "link": result.get("link")} if isinstance(result, dict) and "link" in result else result

def move_file(source_path, destination_path):
    """Move a file within Dropbox."""
    result = make_request("files/move_v2", json_payload={"from_path": source_path, "to_path": destination_path})
    return {"status": "success", "message": f"Moved {source_path} to {destination_path}"} if isinstance(result, dict) and "metadata" in result else result

def main():
    parser = argparse.ArgumentParser(description="Dropbox CLI Tool")
    parser.add_argument("action", choices=["search_files", "download_file", "generate_temporary_link", "move_file", "get_supported_actions"], help="Action to perform")
    parser.add_argument("--params", type=str, help="JSON-encoded parameters for the action")

    args = parser.parse_args()

    if args.action == "get_supported_actions":
        print(json.dumps(get_supported_actions(), indent=4))
        return

    params = json.loads(args.params) if args.params else {}

    if args.action == "search_files":
        result = search_files(params.get("query", ""))
    elif args.action == "download_file":
        result = download_file(params.get("path", ""))
    elif args.action == "generate_temporary_link":
        result = generate_temporary_link(params.get("path", ""))
    elif args.action == "move_file":
        result = move_file(params.get("source_path", ""), params.get("destination_path", ""))
    else:
        result = {"status": "error", "message": "Invalid action"}

    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
