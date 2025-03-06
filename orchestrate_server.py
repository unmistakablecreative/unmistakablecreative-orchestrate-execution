from fastapi import FastAPI, HTTPException
import subprocess
import json
import os
import logging

app = FastAPI()

# Tool configuration files
ORCHESTRATE_TOOLS_PATH = "orchestrate_tools.json"
MARKETPLACE_TOOLS_PATH = "orchestrate_marketplace.json"
ORCHESTRATE_BRAIN_PATH = "orchestrate_brain.json"
ORCHESTRATE_RECALL_PATH = "orchestrate_recall.json"

# Set up logging
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")

def load_tools():
    """Loads tools from all sources and merges them into a single dictionary."""
    tools = {}

    for file_path in [ORCHESTRATE_TOOLS_PATH, MARKETPLACE_TOOLS_PATH, ORCHESTRATE_BRAIN_PATH, ORCHESTRATE_RECALL_PATH]:
        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    tools.update(json.load(file).get("tools", {}))
            else:
                logging.warning(f"{file_path} not found. Skipping.")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logging.warning(f"Failed to load {file_path}: {str(e)}")

    return {"tools": tools}

def run_script(tool_name, action, params):
    """Runs a tool dynamically based on the loaded tools."""
    tools = load_tools().get("tools", {})

    if tool_name not in tools:
        return {"error": f"Tool '{tool_name}' not found."}

    script_path = tools[tool_name]["path"]
    params_json = json.dumps(params)

    try:
        result = subprocess.run(
            ["python3", script_path, action, "--params", params_json],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        return {"error": "Script execution failed", "details": e.stderr}

@app.get("/load_tools")
def load_tools_from_json():
    """Returns all tools from orchestrate_tools.json, orchestrate_marketplace.json, orchestrate_brain.json, and orchestrate_recall.json."""
    return load_tools()

@app.get("/get_supported_actions/{tool_name}")
def get_supported_actions(tool_name: str):
    """Dynamically retrieves supported actions for a given tool."""
    response = run_script(tool_name, "get_supported_actions", {})
    if "error" in response:
        raise HTTPException(status_code=500, detail=response)
    return response

@app.post("/execute_task")
def execute_task(request: dict):
    """Executes a tool action dynamically."""
    tool_name = request.get("tool_name")
    action = request.get("action")
    params = request.get("params", {})

    if not tool_name or not action:
        raise HTTPException(status_code=400, detail="Missing tool_name or action.")

    response = run_script(tool_name, action, params)
    if "error" in response:
        raise HTTPException(status_code=500, detail=response)
    return response
