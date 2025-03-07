import json
import os
import argparse
import requests
import logging

# 🔥 Paths
MARKETPLACE_JSON = "orchestrate_marketplace.json"
TOOLS_JSON = "orchestrate_tools.json"
TOOLS_DIRECTORY = os.getcwd()  # Ensure proper pathing

# 🔥 Configure logging
logging.basicConfig(filename="install_tool.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_json(file_path):
    """Loads a JSON file safely."""
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(file_path, data):
    """Saves data to a JSON file."""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def install_tool(tool_name):
    """Downloads and installs a tool from the GitHub marketplace."""
    marketplace = load_json(MARKETPLACE_JSON)
    tools = load_json(TOOLS_JSON)

    if "tools" not in marketplace or tool_name not in marketplace["tools"]:
        return {"error": f"Tool '{tool_name}' not found in the marketplace."}

    if marketplace["tools"][tool_name].get("installed"):
        return {"error": f"Tool '{tool_name}' is already installed."}

    repo_url = marketplace["tools"][tool_name].get("repo_url")

    if not repo_url:
        return {"error": f"Tool '{tool_name}' does not have a valid GitHub URL."}

    # 🔥 Download the tool from GitHub
    response = requests.get(repo_url)

    if response.status_code != 200:
        return {"error": f"Failed to download '{tool_name}' from {repo_url} (HTTP {response.status_code})."}

    # 🔥 Ensure correct file path
    tool_filename = f"{tool_name}.py"
    tool_path = os.path.join(TOOLS_DIRECTORY, tool_filename)

    with open(tool_path, "w") as f:
        f.write(response.text)

    # 🔥 Register only the relative path in orchestrate_tools.json
    tools.setdefault("tools", {})[tool_name] = {"path": tool_filename}
    save_json(TOOLS_JSON, tools)

    # 🔥 Update marketplace status
    marketplace["tools"][tool_name]["installed"] = True
    save_json(MARKETPLACE_JSON, marketplace)

    logging.info(f"✅ Installed tool: {tool_name} from {repo_url}")
    return {"status": "success", "message": f"✅ '{tool_name}' installed successfully from {repo_url}."}

def uninstall_tool(tool_name):
    """Removes a tool and updates orchestrate_marketplace.json."""
    marketplace = load_json(MARKETPLACE_JSON)
    tools = load_json(TOOLS_JSON)

    if tool_name not in tools.get("tools", {}):
        return {"error": f"Tool '{tool_name}' is not installed."}

    tool_path = os.path.join(TOOLS_DIRECTORY, tools["tools"][tool_name]["path"])
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

def main():
    parser = argparse.ArgumentParser(description="Install Tool")
    parser.add_argument("action", choices=["install", "uninstall"], help="Action to perform")
    parser.add_argument("--params", type=str, help="JSON-encoded parameters")
    args = parser.parse_args()
    params = json.loads(args.params) if args.params else {}

    if args.action == "install":
        if "tool_name" not in params:
            print(json.dumps({"status": "error", "message": "❌ 'tool_name' is required for install."}))
        else:
            print(json.dumps(install_tool(params["tool_name"]), indent=4))

    elif args.action == "uninstall":
        if "tool_name" not in params:
            print(json.dumps({"status": "error", "message": "❌ 'tool_name' is required for uninstall."}))
        else:
            print(json.dumps(uninstall_tool(params["tool_name"]), indent=4))

if __name__ == "__main__":
    main()
