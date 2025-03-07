import requests
import json

SERVER_URL = "http://localhost:5005/execute_task"

tools_to_test = [
    {"tool_name": "gmail_tool", "action": "fetch_unread", "params": {"input": "label:inbox"}},
    {"tool_name": "dropbox_tool", "action": "list_files", "params": {"input": ""}},
    {"tool_name": "readwise_tool", "action": "fetch_highlights", "params": {"input": "Made To Stick"}},
    {"tool_name": "ideogram_tool", "action": "generate_image", "params": {"input": "A futuristic city skyline at sunset", "options": {"aspect_ratio": "ASPECT_16_9"}}},
    {"tool_name": "mailjet_tool", "action": "send_email", "params": {"input": "srini@unmistakablemedia.com", "options": {"subject": "Test Email", "body": "This is a test email from Mailjet."}}}
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
