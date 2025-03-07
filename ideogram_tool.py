import requests
import json
import argparse
import os

CREDENTIALS_FILE = "credentials.json"
IDEOGRAM_URL = "https://api.ideogram.ai/generate"

def load_api_key():
    """Loads API key from credentials.json."""
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            creds = json.load(f)
        return creds.get("ideogram_api_key")
    return None

def execute_action(action, params):
    """Executes an Ideogram API request."""
    api_key = load_api_key()
    if not api_key:
        return {"status": "error", "message": "Missing API key in credentials.json"}
    
    headers = {"Api-Key": api_key, "Content-Type": "application/json"}
    prompt = params.get("input", "")
    options = params.get("options", {})
    aspect_ratio = options.get("aspect_ratio", "ASPECT_16_9")
    model = options.get("model", "V_2")
    
    payload = {"image_request": {"prompt": prompt, "aspect_ratio": aspect_ratio, "model": model}}
    response = requests.post(IDEOGRAM_URL, headers=headers, json=payload)
    
    try:
        return response.json() if response.status_code == 200 else {"status": "error", "message": "API request failed"}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON response from Ideogram."}

def main():
    parser = argparse.ArgumentParser(description="Ideogram Tool")
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
