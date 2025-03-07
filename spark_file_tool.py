import json
import os
import argparse

SPARK_FILE_PATH = "spark_file.json"

def load_spark_file():
    """Loads Spark File data, ensuring 'entries' key exists."""
    if os.path.exists(SPARK_FILE_PATH):
        with open(SPARK_FILE_PATH, "r") as f:
            data = json.load(f)
            if "entries" not in data:
                data["entries"] = []  # Ensure 'entries' exists
            return data
    return {"entries": []}

def save_spark_file(data):
    """Saves updates to Spark File."""
    with open(SPARK_FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)

def execute_action(action, params):
    """Executes Spark File actions."""
    data = load_spark_file()
    
    if action == "add_entry":
        entry = {"content": params.get("input", ""), "category": params.get("options", {}).get("category", "General")}
        data["entries"].append(entry)
        save_spark_file(data)
        return {"status": "success", "message": "Entry added successfully."}
    elif action == "search_entries":
        query = params.get("input", "").lower()
        results = [entry for entry in data["entries"] if query in entry["content"].lower()]
        return {"status": "success", "results": results} if results else {"status": "error", "message": "No matches found."}
    else:
        return {"status": "error", "message": "Invalid action or missing parameters."}

def main():
    parser = argparse.ArgumentParser(description="Spark File Tool")
    parser.add_argument("action", choices=["add_entry", "search_entries"], help="Action to perform")
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
