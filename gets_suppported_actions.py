import os
import json
import subprocess

def get_tool_scripts():
    """Scans the directory and lists all valid tool scripts ending in _tool.py"""
    tools = [
        file for file in os.listdir()
        if file.endswith("_tool.py") and os.path.isfile(file)
    ]
    return tools

def get_supported_actions(tool_script):
    """Runs get_supported_actions for a given tool script"""
    try:
        result = subprocess.run(
            ["python3", tool_script, "get_supported_actions"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return {"error": f"Failed to retrieve actions for {tool_script}"}

def main():
    tools = get_tool_scripts()
    all_actions = {}

    for tool in tools:
        tool_name = tool.replace(".py", "")
        actions = get_supported_actions(tool)
        all_actions[tool_name] = actions

    print(json.dumps(all_actions, indent=4))

if __name__ == "__main__":
    main()
