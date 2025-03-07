import subprocess
import json
import os

REFRACTORED_DIR = "/Users/srinivas/Orchestrate Github/orchestrate-marketplace/Refactored/"

TOOLS_TO_TEST = [
    {"tool_name": "gmail_tool", "action": "fetch_unread", "params": {"input": "label:inbox"}},
    {"tool_name": "dropbox_tool", "action": "list_files", "params": {"input": ""}},
    {"tool_name": "readwise_tool", "action": "fetch_highlights", "params": {"input": "Deep Work"}},
    {"tool_name": "ideogram_tool", "action": "generate_image", "params": {"input": "A futuristic city skyline at sunset", "options": {"aspect_ratio": "ASPECT_16_9"}}},
    {"tool_name": "mailjet_tool", "action": "send_email", "params": {"input": "srini@unmistakablemedia.com", "options": {"subject": "Test Email", "body": "This is a test email from Mailjet."}}},
    {"tool_name": "leonardo_tool", "action": "generate_image", "params": {"input": "A cyberpunk city at night", "options": {"resolution": "1024x1024"}}}
]

def execute_local_script(tool_name, action, params):
    """Executes a script locally before server testing."""
    script_path = os.path.join(REFRACTORED_DIR, f"{tool_name}.py")
    if not os.path.exists(script_path):
        return {"tool": tool_name, "status": "error", "message": f"❌ Script '{tool_name}.py' not found in {REFRACTORED_DIR}"}
    
    params_json = json.dumps(params)
    try:
        result = subprocess.run(
            ["python3", script_path, action, "--params", params_json],
            capture_output=True,
            text=True,
            check=True
        )
        return {"tool": tool_name, "status": "success", "output": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"tool": tool_name, "status": "error", "message": e.stderr.strip()}

def main():
    test_results = []
    for tool in TOOLS_TO_TEST:
        result = execute_local_script(tool["tool_name"], tool["action"], tool["params"])
        test_results.append(result)
    
    print(json.dumps(test_results, indent=4))

if __name__ == "__main__":
    main()
