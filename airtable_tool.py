import requests
import json
import argparse
import os
import sys

# Base URL for Airtable API
BASE_URL = "https://api.airtable.com/v0"

def get_supported_actions():
    """Returns supported actions and required parameters."""
    return {
        "list_records": ["base_id", "table_id", "view_name", "fields"],
        "fetch_record": ["base_id", "table_id", "record_id", "fields"],
        "update_record": ["base_id", "table_id", "record_id", "fields"],
        "create_record": ["base_id", "table_id", "fields"]
    }

def parse_json_fields(fields, expected_type):
    """Parses fields input and ensures it matches the expected type (list or dict)."""
    try:
        fields_data = json.loads(fields)
        if not isinstance(fields_data, expected_type):
            raise ValueError(f"Expected {expected_type.__name__}, got {type(fields_data).__name__}.")
        return fields_data
    except (json.JSONDecodeError, ValueError) as e:
        return {"status": "error", "message": f"Invalid JSON format: {str(e)}"}

def make_request(method, url, headers, params=None, payload=None):
    """Handles API requests to Airtable."""
    try:
        response = requests.request(method, url, headers=headers, params=params, json=payload)
        response_json = response.json() if response.text else {}
    except json.JSONDecodeError:
        return {"status": "error", "message": f"Invalid JSON response: {response.text}"}

    if response.status_code in [200, 201, 204]:
        return {"status": "success", "response": response_json or "No Content"}
    else:
        return {"status": "error", "message": f"Request failed: {response.status_code}", "response": response_json}

def list_records(api_key, base_id, table_id, view_name, fields="[]"):
    """Lists records from the specified table."""
    url = f"{BASE_URL}/{base_id}/{table_id}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    fields_list = parse_json_fields(fields, list)
    if isinstance(fields_list, dict) and "status" in fields_list:
        return fields_list  # Return error message

    params = {"view": view_name, "fields": fields_list} if fields_list else {"view": view_name}
    return make_request("GET", url, headers, params=params)

def fetch_record(api_key, base_id, table_id, record_id, fields="[]"):
    """Fetches a single record by record_id."""
    url = f"{BASE_URL}/{base_id}/{table_id}/{record_id}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    fields_list = parse_json_fields(fields, list)
    if isinstance(fields_list, dict) and "status" in fields_list:
        return fields_list

    params = {"fields": fields_list} if fields_list else None
    return make_request("GET", url, headers, params=params)

def update_record(api_key, base_id, table_id, record_id, fields):
    """Updates a record in the specified table."""
    url = f"{BASE_URL}/{base_id}/{table_id}/{record_id}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    fields_data = parse_json_fields(fields, dict)
    if isinstance(fields_data, dict) and "status" in fields_data:
        return fields_data

    payload = {"fields": fields_data}
    return make_request("PATCH", url, headers, payload=payload)

def create_record(api_key, base_id, table_id, fields):
    """Creates a new record in the specified table."""
    url = f"{BASE_URL}/{base_id}/{table_id}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    fields_data = parse_json_fields(fields, dict)
    if isinstance(fields_data, dict) and "status" in fields_data:
        return fields_data

    payload = {"fields": fields_data}
    return make_request("POST", url, headers, payload=payload)

def main():
    """CLI entry point for Airtable tool execution."""
    parser = argparse.ArgumentParser(description="Airtable Tool CLI")
    parser.add_argument("action", type=str, help="Action to perform (list_records, fetch_record, update_record, create_record)")
    parser.add_argument("base_id", type=str, help="Airtable Base ID")
    parser.add_argument("table_id", type=str, help="Airtable Table ID")
    parser.add_argument("--api_key", type=str, help="Airtable API Key (overrides env variable)")
    parser.add_argument("--record_id", type=str, help="Record ID (for fetch/update actions)")
    parser.add_argument("--view_name", type=str, required=True, help="View Name (for listing records)")
    parser.add_argument("--fields", type=str, default="[]", help="Fields as JSON (e.g., '[\"Name\", \"Email\"]' for list/fetch, '{\"Name\": \"John\"}' for update/create)")

    args = parser.parse_args()

    api_key = args.api_key or os.getenv("AIRTABLE_API_KEY")
    if not api_key:
        print(json.dumps({"status": "error", "message": "Airtable API key missing. Provide --api_key or set AIRTABLE_API_KEY env variable."}))
        sys.exit(1)

    actions = {
        "list_records": list_records,
        "fetch_record": fetch_record,
        "update_record": update_record,
        "create_record": create_record
    }

    if args.action not in actions:
        print(json.dumps({"status": "error", "message": f"Unsupported action: {args.action}"}))
        sys.exit(1)

    params = {k: v for k, v in vars(args).items() if v is not None}
    del params["action"]

    result = actions[args.action](api_key, **params)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
