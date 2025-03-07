import json
import argparse
import os
import shutil

def create_file(file_path, content=""):
    """Creates a file with optional content."""
    try:
        abs_path = os.path.abspath(file_path)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"status": "success", "message": f"✅ File created: {abs_path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def read_file(file_path):
    """Reads a file and returns its content."""
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        return {"status": "error", "message": f"❌ File '{abs_path}' not found."}

    with open(abs_path, "r", encoding="utf-8") as f:
        content = f.read()
    return {"status": "success", "content": content}

def delete_file(file_path):
    """Deletes a file."""
    abs_path = os.path.abspath(file_path)
    if os.path.exists(abs_path):
        os.remove(abs_path)
        return {"status": "success", "message": f"🗑 Deleted: {abs_path}"}
    return {"status": "error", "message": f"❌ File '{abs_path}' not found."}

def search_files(query):
    """Search for files by name."""
    results = []
    search_dir = "/Users/srinivas/"

    for root, _, files in os.walk(search_dir):
        for file in files:
            if query.lower() in file.lower():
                results.append(os.path.join(root, file))

    return {"status": "success", "results": results} if results else {"status": "error", "message": "❌ No files found"}

def get_supported_actions():
    """Returns the supported actions."""
    return {
        "create_file": ["file_path", "content"],
        "read_file": ["file_path"],
        "delete_file": ["file_path"],
        "search_files": ["query"],
        "get_supported_actions": []
    }

def main():
    parser = argparse.ArgumentParser(description="File Manager Tool")
    parser.add_argument("action", choices=["create_file", "read_file", "delete_file", "search_files", "get_supported_actions"], help="Action to perform")
    parser.add_argument("--params", type=str, required=True, help="JSON string containing parameters")

    args = parser.parse_args()

    # ✅ Ensure JSON input is valid
    try:
        params_dict = json.loads(args.params)
    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "Invalid JSON format in --params."}, indent=4))
        return

    if args.action == "get_supported_actions":
        print(json.dumps(get_supported_actions(), indent=4))
        return

    actions = get_supported_actions()

    if args.action not in actions:
        print(json.dumps({"status": "error", "message": f"Invalid action: {args.action}"}))
        return

    # ✅ Call the function dynamically
    result = globals()[args.action](**params_dict)
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
