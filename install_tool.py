import json
import os
import argparse
import requests
import logging
from typing import Dict, Any

# 🔥 Paths
MARKETPLACE_JSON = "orchestrate_marketplace.json"
TOOLS_JSON = "orchestrate_tools.json"
TOOLS_DIRECTORY = "."  # Adjust if needed

# 🔥 Configure logging
logging.basicConfig(filename="install_tool.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_json(file_path: str) -> Dict[str, Any]:
    """Safely loads a JSON file."""
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(file_path: str, data: Dict[str, Any]):
    """Safely saves JSON data."""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def install_tool(tool_name: str) -> Dict[str, Any]:
    """Installs a tool from the GitHub marketplace."""
    marketplace = load_json(MARKETPLACE_JSON)
    tools = load_json(TOOLS_JSON)

    if tool_name not in marketplace.get("tools", {}):
        return {"error": f"Tool '{tool_name}' not found in the marketplace."}

    if marketplace["tools"][tool_name].get("installed"):
        return {"error": f"Tool '{tool_name}' is already installed."}

    repo_url = marketplace["tools"][tool_name].get("repo_url")
    if not repo_url:
        return {"error": f"Tool '{tool_name}' does not have a valid GitHub URL."}

    # 🔥 Download the tool script
    response = requests.get(repo_url)
    if response.status_code != 200:
        return {"error": f"Failed to download '{tool_name}' from {repo_url} (HTTP {response.status_code})."}

    # 🔥 Save the tool script
    tool_filename = f"{tool_name}.py"
    tool_path = os.path.join(TOOLS_DIRECTORY, tool_filename)

    with open(tool_path, "w") as f:
        f.write(response.text)

    # 🔥 Register the tool
    tools.setdefault("tools", {})[tool_name] = {"path": tool_path}
    save_json(TOOLS_JSON, tools)

    # 🔥 Update marketplace status
    marketplace["tools"][tool_name]["installed"] = True
    save_json(MARKETPLACE_JSON, marketplace)

    logging.info(f"✅ Installed tool: {tool_name}")
    return {"status": "success", "message": f"✅ '{tool_name}' installed successfully from {repo_url}."}

def uninstall_tool(tool_name: str) -> Dict[str, Any]:
    """Uninstalls a tool by removing its file and updating JSONs."""
    marketplace = load_json(MARKETPLACE_JSON)
    tools = load_json(TOOLS_JSON)

    if tool_name not in tools.get("tools", {}):
        return {"error": f"Tool '{tool_name}' is not installed."}

    tool_path = tools["tools"][tool_name]["path"]

    # 🔥 Remove tool file
    if os.path.exists(tool_path):
        os.remove(tool_path)

    # 🔥 Remove from orchestrate_tools.json
    del tools["tools"][tool_name]
    save_json(TOOLS_JSON, tools)

    # 🔥 Update marketplace status
    if "tools" in marketplace and tool_name in marketplace["tools"]:
        marketplace["tools"][tool_name]["installed"] = False
        save_json(MARKETPLACE_JSON, marketplace)

    logging.info(f"❌ Uninstalled tool: {tool_name}")
    return {"status": "success", "message": f"❌ '{tool_name}' uninstalled successfully."}

def get_supported_actions() -> Dict[str, Any]:
    """Returns supported actions for Orchestrate compliance."""
    return {
        "install": ["tool_name"],
        "uninstall": ["tool_name"],
        "get_supported_actions": []
    }

def execute_action(action: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handles execution of install, uninstall, and get_supported_actions."""
    if action == "install":
        return install_tool(params.get("tool_name", ""))
    elif action == "uninstall":
        return uninstall_tool(params.get("tool_name", ""))
    elif action == "get_supported_actions":
        return get_supported_actions()
    else:
        return {"error": f"Invalid action '{action}'."}

def main():
    parser = argparse.ArgumentParser(description="Install Tool for Orchestrate")
    parser.add_argument("action", type=str, choices=["install", "uninstall", "get_supported_actions"], help="Action to perform")
    parser.add_argument("--params", type=str, help="JSON-encoded parameters")

    args = parser.parse_args()
    params = json.loads(args.params) if args.params else {}

    print(json.dumps(execute_action(args.action, params), indent=4))

if __name__ == "__main__":
    main()
