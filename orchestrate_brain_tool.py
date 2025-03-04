import json
import os
import argparse
import logging

logging.basicConfig(level=logging.INFO)

BRAIN_PATH = os.path.join(os.getcwd(), "orchestrate_brain.json")

def load_brain():
    """Load the orchestrate_brain.json file."""
    if not os.path.exists(BRAIN_PATH):
        return {}
    with open(BRAIN_PATH, "r") as file:
        return json.load(file)

def save_brain(brain):
    """Save updates to orchestrate_brain.json."""
    with open(BRAIN_PATH, "w") as file:
        json.dump(brain, file, indent=4)
    logging.info("Orchestrate Brain successfully updated.")

def get_supported_actions():
    """Return supported actions as a JSON dictionary."""
    return {
        "update_field": ["update_path", "new_value"],
        "add_field": ["update_path", "new_value"],
        "remove_field": ["update_path"],
        "search_brain": ["query"]
    }

def search_brain(query):
    """Recursively search for a key or value in orchestrate_brain.json."""
    brain = load_brain()
    matches = {}

    def recursive_search(data, path=""):
        """Recursively search through JSON data."""
        if isinstance(data, dict):
            for key, value in data.items():
                full_path = f"{path}.{key}" if path else key
                if query.lower() in key.lower() or (isinstance(value, str) and query.lower() in value.lower()):
                    matches[full_path] = value
                recursive_search(value, full_path)

    recursive_search(brain)
    return matches if matches else {"message": "No matches found."}

def update_field(update_path, new_value):
    """Update an existing field in orchestrate_brain.json (supports dot notation)."""
    brain = load_brain()
    keys = update_path.split(".")
    ref = brain

    for key in keys[:-1]:
        if key in ref and isinstance(ref[key], dict):
            ref = ref[key]
        else:
            return {"success": False, "error": f"Field '{update_path}' not found."}

    last_key = keys[-1]
    if last_key in ref:
        ref[last_key] = new_value
        save_brain(brain)
        return {"success": True, "message": f"Updated '{update_path}' to '{new_value}'."}
    return {"success": False, "error": f"Field '{update_path}' not found."}

def add_field(update_path, new_value):
    """Add a new field to orchestrate_brain.json (supports dot notation)."""
    brain = load_brain()
    keys = update_path.split(".")
    ref = brain

    for key in keys[:-1]:
        if key not in ref or not isinstance(ref[key], dict):
            ref[key] = {}
        ref = ref[key]

    last_key = keys[-1]
    if last_key in ref:
        return {"success": False, "error": f"Field '{update_path}' already exists."}

    ref[last_key] = new_value
    save_brain(brain)
    return {"success": True, "message": f"Added '{update_path}'."}

def remove_field(update_path):
    """Remove a field from orchestrate_brain.json (supports dot notation)."""
    brain = load_brain()
    keys = update_path.split(".")
    ref = brain

    for key in keys[:-1]:
        if key in ref and isinstance(ref[key], dict):
            ref = ref[key]
        else:
            return {"success": False, "error": f"Field '{update_path}' not found."}

    last_key = keys[-1]
    if last_key in ref:
        del ref[last_key]
        save_brain(brain)
        return {"success": True, "message": f"Removed '{update_path}'."}

    return {"success": False, "error": f"Field '{update_path}' not found."}

def execute_action(action, params):
    """Execute the given action with provided parameters."""
    if action == "get_supported_actions":
        return get_supported_actions()
    elif action == "search_brain":
        return search_brain(params.get("query", ""))
    elif action == "update_field":
        return update_field(params.get("update_path", ""), params.get("new_value", ""))
    elif action == "add_field":
        return add_field(params.get("update_path", ""), params.get("new_value", ""))
    elif action == "remove_field":
        return remove_field(params.get("update_path", ""))
    return {"error": "Invalid action."}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Orchestrate Brain Tool - CLI JSON Manager")
    parser.add_argument("action", type=str, help="Action to perform")
    parser.add_argument("--params", type=str, help="JSON-formatted string of parameters", default="{}")

    args = parser.parse_args()

    try:
        params = json.loads(args.params)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON format in --params"}, indent=4))
        exit(1)

    result = execute_action(args.action, params)
    print(json.dumps(result, indent=4))
