import subprocess
import json
import argparse
import os

REFRACTORED_DIR = "/Users/srinivas/Orchestrate Github/orchestrate-marketplace/Refactored/"

def execute_local_script(tool_name, action, params):
    """Executes a script locally before testing on the server."""
    script_path = os.path.join(REFRACTORED_DIR, f"{tool_name}.py")
    if not os.path.exists(script_path):
        return {"status": "error", "message": f"❌ Script '{tool_name}.py' not found in {REFRACTORED_DIR}"}
    
    params_json = json.dumps(params)
    try:
        result = subprocess.run(
            ["python3", script_path, action, "--params", params_json],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr.strip()}

def main():
    parser = argparse.ArgumentParser(description="Local Script Executor")
    parser.add_argument("tool_name", help="Tool script to execute")
    parser.add_argument("action", help="Action to perform")
    parser.add_argument("--params", type=str, required=True, help="JSON-encoded parameters")
    args = parser.parse_args()
    
    try:
        params_dict = json.loads(args.params)
    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "Invalid JSON format."}, indent=4))
        return
    
    result = execute_local_script(args.tool_name, args.action, params_dict)
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
