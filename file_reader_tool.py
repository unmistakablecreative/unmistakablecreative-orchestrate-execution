import json
import os
import argparse

CREDENTIALS_FILE = "credentials.json"
BASE_DIR = os.getcwd()

def read_file(filename):
    """Reads content from a file in BASE_DIR."""
    file_path = os.path.join(BASE_DIR, filename)
    
    if not os.path.exists(file_path):
        return {"status": "error", "message": f"❌ File '{filename}' not found."}
    
    with open(file_path, "r") as f:
        content = f.read()
    
    return {"status": "success", "content": content}

def execute_action(action, params):
    """Executes file read operations."""
    filename = params.get("input", "")
    
    if not filename:
        return {"status": "error", "message": "❌ 'filename' is required."}
    
    return read_file(filename)

def main():
    parser = argparse.ArgumentParser(description="File Reader Tool")
    parser.add_argument("action", choices=["read_file"], help="Action to perform")
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
