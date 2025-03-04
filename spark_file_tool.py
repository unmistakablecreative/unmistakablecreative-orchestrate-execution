import json
import os
import argparse
import logging
from datetime import datetime

SPARK_FILE_PATH = "spark_file.json"
ARCHIVE_FILE_PATH = "spark_file_archive.json"
MAX_FILE_SIZE_MB = 5  # Set file size limit to 5MB

# Configure logging
logging.basicConfig(filename="spark_file_tool.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def ensure_spark_file_exists():
    """Ensure the JSON file exists and initialize if necessary."""
    if not os.path.exists(SPARK_FILE_PATH):
        with open(SPARK_FILE_PATH, "w") as f:
            json.dump({"swipe_file": []}, f, indent=4)

def read_spark_file():
    """Read and return the JSON data from the Spark File."""
    with open(SPARK_FILE_PATH, "r") as f:
        return json.load(f)

def write_spark_file(data):
    """Write updated JSON data back to the Spark File."""
    with open(SPARK_FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)

def archive_old_entries():
    """Archive old entries if the file size exceeds the limit."""
    if os.path.exists(SPARK_FILE_PATH) and os.path.getsize(SPARK_FILE_PATH) > MAX_FILE_SIZE_MB * 1024 * 1024:
        logging.warning("⚠️ File size exceeded 5MB. Archiving old entries.")
        data = read_spark_file()
        
        # Move half of the oldest entries to the archive file
        archive_data = data["swipe_file"][:len(data["swipe_file"]) // 2]
        with open(ARCHIVE_FILE_PATH, "a") as f:
            json.dump(archive_data, f, indent=4)
            f.write("\n")
        
        # Keep only the latest half in the main file
        data["swipe_file"] = data["swipe_file"][len(data["swipe_file"]) // 2:]
        write_spark_file(data)

def add_entry(content, category="General", source="User Command"):
    """Add an entry to the Spark File."""
    ensure_spark_file_exists()
    archive_old_entries()
    
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "category": category,
        "content": content,
        "source": source
    }

    data = read_spark_file()
    data["swipe_file"].append(entry)
    write_spark_file(data)

    logging.info(f"✅ Entry added: {entry}")
    return {"status": "success", "message": "✅ Entry added to Spark File."}

def search_entries(keyword):
    """Search for entries containing the given keyword."""
    ensure_spark_file_exists()
    
    data = read_spark_file()
    matches = [entry for entry in data["swipe_file"] if keyword.lower() in entry["content"].lower()]
    
    logging.info(f"🔍 Search performed for '{keyword}'. Matches found: {len(matches)}")
    return matches if matches else {"status": "error", "message": "No matches found."}

def show_all_entries():
    """Return all entries from the Spark File."""
    ensure_spark_file_exists()
    
    logging.info("📜 Retrieved all entries.")
    return {"status": "success", "entries": read_spark_file()["swipe_file"]}

def get_supported_actions():
    """Return supported actions and their parameters."""
    return {
        "add_entry": ["content", "category", "source"],
        "search_entries": ["keyword"],
        "show_all_entries": []
    }

def main():
    parser = argparse.ArgumentParser(description="Spark File Tool")
    parser.add_argument("action", type=str, choices=["add_entry", "search_entries", "show_all_entries", "get_supported_actions"],
                        help="Action to perform")
    parser.add_argument("--params", type=str, help="JSON-encoded parameters for the action")

    args = parser.parse_args()

    # ✅ Parse JSON parameters correctly
    params = json.loads(args.params) if args.params else {}

    if args.action == "add_entry":
        if "content" not in params:
            print(json.dumps({"status": "error", "message": "❌ 'content' is required for add_entry."}))
        else:
            result = add_entry(params["content"], params.get("category", "General"), params.get("source", "User Command"))
            print(json.dumps(result, indent=4))

    elif args.action == "search_entries":
        if "keyword" not in params:
            print(json.dumps({"status": "error", "message": "❌ 'keyword' is required for search_entries."}))
        else:
            result = search_entries(params["keyword"])
            print(json.dumps(result, indent=4))

    elif args.action == "show_all_entries":
        print(json.dumps(show_all_entries(), indent=4))

    elif args.action == "get_supported_actions":
        print(json.dumps(get_supported_actions(), indent=4))

if __name__ == "__main__":
    main()
