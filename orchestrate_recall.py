import json
import os
import argparse
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

def main():
    parser = argparse.ArgumentParser(description="Orchestrate Recall Tool")
    parser.add_argument("action", choices=["add_entry", "search_entries", "show_all_entries"], help="Action to perform")
    parser.add_argument("--params", type=str, help="JSON-encoded parameters for the action")

    args = parser.parse_args()
    params = json.loads(args.params) if args.params else {}

    if args.action == "add_entry":
        result = add_entry(params.get("content", ""), params.get("context", "General"))
    elif args.action == "search_entries":
        result = search_entries(params.get("keyword", ""))
    elif args.action == "show_all_entries":
        result = show_all_entries()
    else:
        result = {"status": "error", "message": "Invalid action."}
    
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
