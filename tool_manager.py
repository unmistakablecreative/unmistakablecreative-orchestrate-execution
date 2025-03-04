import argparse
import json
import os

# Correct file path for managing tools
TOOL_CONFIG_PATH = "orchestrate_tools.json"

def load_tools():
    """Load the current tool configuration from orchestrate_tools.json."""
    if not os.path.exists(TOOL_CONFIG_PATH):
        return {"tools": {}}

    with open(TOOL_CONFIG_PATH, "r") as f:
        return json.load(f)

def save_tools(tools):
    """Save updated tools to orchestrate_tools.json."""
    with open(TOOL_CONFIG_PATH, "w") as f:
        json.dump(tools, f, indent=4)

def get_supported_actions():
    """Return the list of supported actions."""
    return {
        "add_tool": ["tool_name", "script_path"],
        "remove_tool": ["tool_name"],
        "list_tools": []
    }

def add_tool(tool_name, script_path):
    """Add a new tool to orchestrate_tools.json."""
    tools = load_tools()

    if tool_name in tools["tools"]:
        return {"status": "error", "message": f"❌ Tool '{tool_name}' already exists."}

    tools["tools"][tool_name] = {"path": script_path}
    save_tools(tools)

    return {"status": "success", "message": f"✅ Tool '{tool_name}' added successfully."}

def remove_tool(tool_name):
    """Remove a tool from orchestrate_tools.json."""
    tools = load_tools()

    if tool_name not in tools["tools"]:
        return {"status": "error", "message": f"❌ Tool '{tool_name}' not found."}

    del tools["tools"][tool_name]
    save_tools(tools)

    return {"status": "success", "message": f"✅ Tool '{tool_name}' removed successfully."}

def list_tools():
    """List all registered tools."""
    tools = load_tools()
    return {"status": "success", "tools": tools["tools"]}

def main():
    parser = argparse.ArgumentParser(description="Orchestrate Tool Manager")
    parser.add_argument("action", choices=["get_supported_actions", "add_tool", "remove_tool", "list_tools"], help="Action to perform")
    parser.add_argument("--params", type=str, required=False, help="JSON-encoded parameters for the action")

    args = parser.parse_args()

    if args.action == "get_supported_actions":
        print(json.dumps(get_supported_actions(), indent=4))
        return

    # ✅ Parse JSON parameters
    try:
        params = json.loads(args.params) if args.params else {}
    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "Invalid JSON format in --params."}, indent=4))
        return

    # ✅ Execute the selected action
    actions = {
        "add_tool": lambda p: add_tool(p["tool_name"], p["script_path"]),
        "remove_tool": lambda p: remove_tool(p["tool_name"]),
        "list_tools": lambda _: list_tools()
    }

    if args.action in actions:
        result = actions[args.action](params)
        print(json.dumps(result, indent=4))
    else:
        print(json.dumps({"status": "error", "message": f"❌ Unsupported action: {args.action}"}))

if __name__ == "__main__":
    main()
