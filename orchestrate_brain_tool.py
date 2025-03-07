import json
import os
import argparse

BRAIN_FILE = "orchestrate_brain.json"

def load_brain():
    """Loads the Orchestrate Brain JSON data, ensuring proper structure."""
    if os.path.exists(BRAIN_FILE):
        with open(BRAIN_FILE, "r") as f:
            data = json.load(f)
            return data.get("orchestrate_brain", {}).get("operating_logic", {})  # ✅ Corrected search path
    return {}

def save_brain(data):
    """Saves updates to the Orchestrate Brain JSON file."""
    full_data = {"orchestrate_brain": {"operating_logic": data}}
    with open(BRAIN_FILE, "w") as f:
        json.dump(full_data, f, indent=4)

def execute_action(action, params):
    """Executes an Orchestrate Brain action."""
    data = load_brain()
    
    if action == "add_insight":
        category = params.get("input", "")
        content = params.get("options", {}).get("content", "")
        if category not in data:
            data[category] = []
        data[category].append(content)
        save_brain(data)
        return {"status": "success", "message": "Insight added successfully."}
    elif action == "fetch_insights":
        category = params.get("input", "")
        insights = data.get(category, [])
        return {"status": "success", "insights": insights} if insights else {"status": "error", "message": "No insights found."}
    else:
        return {"status": "error", "message": "Invalid action or missing parameters."}

def main():
    parser = argparse.ArgumentParser(description="Orchestrate Brain Tool")
    parser.add_argument("action", choices=["add_insight", "fetch_insights"], help="Action to perform")
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
