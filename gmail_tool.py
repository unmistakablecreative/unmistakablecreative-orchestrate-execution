import json
import os
import argparse
import base64
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

def load_credentials():
    """Loads OAuth credentials from credentials.json."""
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            creds = json.load(f)
        return Credentials(
            token=creds.get("gmail_access_token"),
            refresh_token=creds.get("gmail_refresh_token"),
            client_id=creds.get("gmail_client_id"),
            client_secret=creds.get("gmail_client_secret"),
            token_uri=creds.get("gmail_token_uri")
        )
    return None

def execute_action(action, params):
    """Executes a Gmail API action."""
    creds = load_credentials()
    if not creds:
        return {"status": "error", "message": "Missing OAuth token. Authenticate first."}
    
    service = build("gmail", "v1", credentials=creds)
    email_query = params.get("input", "")
    
    try:
        if action == "fetch_unread":
            results = service.users().messages().list(userId="me", q=email_query).execute()
            messages = results.get("messages", [])
            return {"status": "success", "emails": messages}
        else:
            return {"status": "error", "message": "Invalid action or missing parameters."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Gmail Tool")
    parser.add_argument("action", help="Action to perform")
    parser.add_argument("--params", type=str, required=True, help="JSON-encoded parameters")
    args = parser.parse_args()
    
    try:
        params_dict = json.loads(args.params)
    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "Invalid JSON format."}, indent=4))
        return
    
    result = execute_action(args.action, params_dict)
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
