import json
import os
import argparse

CREDENTIALS_FILE = "credentials.json"
BASE_DIR = os.getcwd()

def ensure_base_dir():
    """Ensure the base directory exists."""
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

def write_file(filename, content, mode="w"):
    """Writes or appends to a file in the BASE_DIR."""
    ensure_base_dir()
    file_path = os.path.join(BASE_DIR, filename)
    
    with open(file_path, mode) as f:
        f.write(content + "\n")  # Add newline for readability
    
    return {"status": "success", "message": f"✅ File '{filename}' updated successfully."}

def execute_action(action, params):
    """Executes file operations."""
    filename = params.get("filename", "")  # ✅ Fixed key
    content = params.get("options", {}).get("content", "")
    mode = params.get("options", {}).get("mode", "w")
    
    if not filename:
        return {"status": "error", "message": "❌ 'filename' is required."}
    
    return write_file(filename, content, mode)

def main():
    parser = argparse.ArgumentParser(description="VS Code Tool")
    parser.add_argument("action", choices=["write_file"], help="Action to perform")
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
