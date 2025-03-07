import argparse
import json
import os

CREDENTIALS_FILE = "credentials.json"
ROADMAP_FILE = "roadmap.json"

def load_roadmap():
    """Load the current roadmap from JSON."""
    if not os.path.exists(ROADMAP_FILE):
        return {"In Development": []}
    with open(ROADMAP_FILE, "r") as f:
        return json.load(f)

def save_roadmap(roadmap):
    """Save the updated roadmap to JSON."""
    with open(ROADMAP_FILE, "w") as f:
        json.dump(roadmap, f, indent=4)

def execute_action(action, params):
    """Executes a roadmap management action."""
    roadmap = load_roadmap()
    
    if action == "add_feature":
        feature, description, eta = params.get("input"), params.get("options", {}).get("description"), params.get("options", {}).get("eta")
        if not feature or not description or not eta:
            return {"status": "error", "message": "Missing required fields."}
        if "In Development" not in roadmap:
            roadmap["In Development"] = []
        if any(f["feature"] == feature for f in roadmap["In Development"]):
            return {"status": "error", "message": f"Feature '{feature}' already exists."}
        roadmap["In Development"].append({"feature": feature, "description": description, "eta": eta})
        save_roadmap(roadmap)
        return {"status": "success", "message": f"Feature '{feature}' added successfully."}
    elif action == "update_feature":
        feature, new_description, new_eta = params.get("input"), params.get("options", {}).get("new_description"), params.get("options", {}).get("new_eta")
        for f in roadmap.get("In Development", []):
            if f["feature"] == feature:
                if new_description:
                    f["description"] = new_description
                if new_eta:
                    f["eta"] = new_eta
                save_roadmap(roadmap)
                return {"status": "success", "message": f"Feature '{feature}' updated successfully."}
        return {"status": "error", "message": f"Feature '{feature}' not found."}
    elif action == "list_features":
        return {"status": "success", "roadmap": roadmap}
    else:
        return {"status": "error", "message": "Invalid action or missing parameters."}

def main():
    parser = argparse.ArgumentParser(description="Roadmap Tool")
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
