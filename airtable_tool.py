import requests
import json
import argparse
import os

BASE_URL = "https://api.airtable.com/v0"
CREDENTIALS_FILE = "credentials.json"

def load_api_key():
    """Loads API key from credentials.json."""
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            creds = json.load(f)
        return creds.get("airtable_api_key")
    return None

def make_request(method, url, params=None, payload=None):
    """Handles API requests to Airtable."""
    api_key = load_api_key()
    if not api_key:
        return {"status": "error", "message": "Missing API key in credentials.json"}
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    response = requests.request(method, url, headers=headers, params=params, json=payload)
    
    try:
        response_json = response.json() if response.text else {}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON response from Airtable."}
    
    if response.status_code in [200, 201, 204]:
        return {"status": "success", "response": response_json or "No Content"}
    else:
        return {"status": "error", "message": f"Request failed: {response.status_code}", "response": response_json}

def execute_action(action, params):
    """Executes an Airtable API action based on input parameters."""
    base_id, table_id = params.get("input", "").split("/")[:2]
    record_id = params.get("record_id", "")
    fields = params.get("options", {}).get("fields", {})
    
    if action == "list_records":
        return make_request("GET", f"{BASE_URL}/{base_id}/{table_id}", params={"view": "Grid view"})
    elif action == "fetch_record" and record_id:
        return make_request("GET", f"{BASE_URL}/{base_id}/{table_id}/{record_id}")
    elif action == "update_record" and record_id:
        return make_request("PATCH", f"{BASE_URL}/{base_id}/{table_id}/{record_id}", payload={"fields": fields})
    elif action == "create_record":
        return make_request("POST", f"{BASE_URL}/{base_id}/{table_id}", payload={"fields": fields})
    else:
        return {"status": "error", "message": "Invalid action or missing parameters."}

def main():
    parser = argparse.ArgumentParser(description="Airtable Tool")
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
