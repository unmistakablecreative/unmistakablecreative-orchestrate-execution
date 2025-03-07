import requests
import json
import argparse
import os

CREDENTIALS_FILE = "credentials.json"
MAILJET_URL = "https://api.mailjet.com/v3.1/send"

def load_api_key():
    """Loads Mailjet API credentials from credentials.json."""
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            creds = json.load(f)
        return creds.get("mailjet_api_key"), creds.get("mailjet_api_secret")
    return None, None

def execute_action(action, params):
    """Executes a Mailjet API request."""
    api_key, api_secret = load_api_key()
    if not api_key or not api_secret:
        return {"status": "error", "message": "Missing API credentials in credentials.json"}
    
    headers = {"Content-Type": "application/json"}
    email_data = {
        "Messages": [
            {
                "From": {"Email": "no-reply@yourdomain.com", "Name": "Your Brand"},
                "To": [{"Email": params.get("input", ""), "Name": "Recipient"}],
                "Subject": params.get("options", {}).get("subject", "No Subject"),
                "TextPart": params.get("options", {}).get("body", "")
            }
        ]
    }
    
    response = requests.post(MAILJET_URL, auth=(api_key, api_secret), headers=headers, json=email_data)
    
    try:
        return response.json() if response.status_code == 200 else {"status": "error", "message": "API request failed"}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON response from Mailjet."}

def main():
    parser = argparse.ArgumentParser(description="Mailjet Tool")
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
