import argparse
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_supported_actions():
    """Return the list of supported actions and required parameters."""
    return {
        "read_file": ["file_path"]
    }

def read_file(file_path):
    """Reads the full content of a file."""
    try:
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"❌ ERROR: File not found - {file_path}"}

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        logging.info(f"✅ File read successfully: {file_path}")
        return {"status": "success", "content": content}

    except Exception as e:
        logging.error(f"❌ ERROR reading file {file_path}: {str(e)}")
        return {"status": "error", "message": str(e)}

def main():
    parser = argparse.ArgumentParser(description="File Reader Tool")
    parser.add_argument("action", choices=["get_supported_actions", "read_file"], help="Action to perform")
    parser.add_argument("--params", type=str, required=False, help="JSON-encoded parameters for the action")

    args = parser.parse_args()

    if args.action == "get_supported_actions":
        print(json.dumps(get_supported_actions(), indent=4))
        return

    # ✅ Parse JSON parameters
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "Invalid JSON format in --params."}, indent=4))
        return

    # ✅ Execute the selected action
    actions = {
        "read_file": read_file
    }

    if args.action in actions:
        result = actions[args.action](**params)
        print(json.dumps(result, indent=4))
    else:
        print(json.dumps({"status": "error", "message": f"❌ Unsupported action: {args.action}"}))

if __name__ == "__main__":
    main()
