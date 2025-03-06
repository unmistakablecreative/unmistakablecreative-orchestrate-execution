import json
import argparse
import os
from datetime import datetime

RECALL_FILE = "orchestrate_recall.json"

def ensure_recall_file():
    """Ensure the recall file exists."""
    if not os.path.exists(RECALL_FILE):
        with open(RECALL_FILE, "w") as f:
            json.dump({"entries": []}, f)

def read_recall():
    """Read entries from the recall file."""
    with open(RECALL_FILE, "r") as f:
        return json.load(f)

def write_recall(data):
    """Write entries to the recall file."""
    with open(RECALL_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_entry(content, context=None):
    """Add an entry to Orchestrate Recall."""
    ensure_recall_file()
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "content": content,
        "context": context or "General"
    }

    data = read_recall()
    data["entries"].append(entry)
    write_recall(data)

    return {"status": "success", "message": "✅ Entry added to Orchestrate Recall."}

def search_entries(keyword):
    """Search for entries containing the given keyword."""
    ensure_recall_file()
    
    data = read_recall()
    matches = [entry for entry in data["entries"] if keyword.lower() in entry["content"].lower()]
    
    return matches if matches else {"status": "error", "message": "No matches found."}

def show_all_entries():
    """Return all entries from Orchestrate Recall."""
    ensure_recall_file()
    return {"status": "success", "entries": read_recall()["entries"]}

def get_supported_actions():
    """Return supported actions and their parameters."""
    return {
        "add_entry": ["content", "context"],
        "search_entries": ["keyword"],
        "show_all_entries": [],
        "get_supported_actions": []
    }

def main():
    parser = argparse.ArgumentParser(description="Orchestrate Recall Tool")
    parser.add_argument("action", type=str, choices=["add_entry", "search_entries", "show_all_entries", "get_supported_actions"],
                        help="Action to perform")
    parser.add_argument("--params", type=str, help="JSON-encoded parameters for the action")

    args = parser.parse_args()
    params = json.loads(args.params) if args.params else {}

    if args.action == "add_entry":
        if "content" not in params:
            print(json.dumps({"status": "error", "message": "❌ 'content' is required for add_entry."}, indent=4))
        else:
            result = add_entry(params["content"], params.get("context", "General"))
            print(json.dumps(result, indent=4))

    elif args.action == "search_entries":
        if "keyword" not in params:
            print(json.dumps({"status": "error", "message": "❌ 'keyword' is required for search_entries."}, indent=4))
        else:
            result = search_entries(params["keyword"])
            print(json.dumps(result, indent=4))

    elif args.action == "show_all_entries":
        print(json.dumps(show_all_entries(), indent=4))

    elif args.action == "get_supported_actions":
        print(json.dumps(get_supported_actions(), indent=4))  # ✅ Now properly executed

if __name__ == "__main__":
    main()
