from fastapi import FastAPI, HTTPException
import subprocess
import json
import os

app = FastAPI()

ORCHESTRATE_TOOLS_PATH = "orchestrate_tools.json"

def load_tools():
    """Loads all tools from orchestrate_tools.json."""
    try:
        with open(ORCHESTRATE_TOOLS_PATH, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"error": "orchestrate_tools.json not found."}

def run_script(tool_name, action, params):
    """Runs a tool dynamically based on orchestrate_tools.json."""
    tools = load_tools().get("tools", {})

    if tool_name not in tools:
        return {"error": f"Tool '{tool_name}' not found in orchestrate_tools.json."}

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
    """Returns all tools from orchestrate_tools.json."""
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
