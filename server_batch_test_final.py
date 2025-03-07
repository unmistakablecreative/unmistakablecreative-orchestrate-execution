import requests
import json

SERVER_URL = "http://localhost:5005/execute_task"

tools_to_test = [
    {"tool_name": "install_tool", "action": "install", "params": {"tool_name": "readwise_tool"}},
    {"tool_name": "create_workflow_tool", "action": "add_workflow", "params": {"workflow_name": "test_workflow", "workflow_config": {"description": "Test workflow", "steps": [{"action": "list_tasks", "tool": "task_tool", "params": {}}]}}}
]

def execute_server_test(tool_name, action, params):
    """Sends a request to the Orchestrate API server to execute a tool action."""
    payload = {
        "tool_name": tool_name,
        "action": action,
        "params": params
    }
    
    response = requests.post(SERVER_URL, json=payload)
    try:
        return response.json()
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON response from server."}

def main():
    test_results = []
    for tool in tools_to_test:
        result = execute_server_test(tool["tool_name"], tool["action"], tool["params"])
        test_results.append({"tool": tool["tool_name"], "status": result.get("status", "error"), "output": result})
    
    print(json.dumps(test_results, indent=4))

if __name__ == "__main__":
    main()
