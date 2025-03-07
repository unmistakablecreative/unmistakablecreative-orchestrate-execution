import json
import os
import subprocess
import argparse
from datetime import datetime

RESULTS_FILE = "tool_test_results.json"
SERVER_URL = "http://localhost:5001/execute-task"

def load_existing_results():
    """Load existing results if file exists, else return empty dict."""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}  # In case of corruption, start fresh
    return {}

def get_supported_actions(tool_name):
    """Fetch supported actions from the tool."""
    try:
        result = subprocess.run(
            ["python", tool_name, "get_supported_actions"],
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout) if result.stdout else {}
    except Exception as e:
        return {"error": str(e)}

def execute_local(tool_name, action, params={}):
    """Execute a specific action locally with given params."""
    try:
        params_json = json.dumps(params)
        result = subprocess.run(
            ["python", tool_name, action, "--params", params_json],
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout) if result.stdout else {"error": "No output"}
    except Exception as e:
        return {"error": str(e)}

def execute_api(tool_name, action, params={}):
    """Execute a specific action via API (cURL to 5001)."""
    try:
        request_body = json.dumps({"tool": tool_name.replace(".py", ""), "task": action, "params": params})
        result = subprocess.run(
            ["curl", "-X", "POST", SERVER_URL, "-H", "Content-Type: application/json", "-d", request_body],
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout) if result.stdout else {"error": "No output"}
    except Exception as e:
        return {"error": str(e)}

def run_tests(tool_name):
    """Run all tool actions both locally and via API, storing results with metadata."""
    timestamp = datetime.utcnow().isoformat()
    actions = get_supported_actions(tool_name)

    if "error" in actions:
        print(f"Error fetching actions: {actions['error']}")
        return

    results = load_existing_results()

    if tool_name not in results:
        results[tool_name] = []

    test_entry = {
        "tested_at": timestamp,
        "results": {}
    }

    for action, required_params in actions.items():
        print(f"🛠  Testing: {action}...")
        params = {param: "test_value" for param in required_params}

        test_entry["results"][action] = {
            "local": execute_local(tool_name, action, params),
            "api": execute_api(tool_name, action, params),
        }

    results[tool_name].append(test_entry)

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"✅ All results saved to {RESULTS_FILE}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Orchestrate Tool Tester")
    parser.add_argument("tool_name", type=str, help="The name of the tool script (e.g., task_tool.py)")
    args = parser.parse_args()
    run_tests(args.tool_name)
