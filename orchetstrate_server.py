from fastapi import FastAPI, HTTPException, Request
import subprocess
import json
import os
import logging

app = FastAPI()

# Tool configuration files
ORCHESTRATE_TOOLS_PATH = "orchestrate_tools.json"  # ✅ Execution only from here
LOAD_SKILLS_FILES = [
    "orchestrate_marketplace.json",
    "orchestrate_brain.json",
    "orchestrate_recall.json"
]  # ✅ Load these for skill availability

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_skills():
    """Loads skills from marketplace, brain, and recall files."""
    merged_skills = {"skills": {}}

    for file_path in LOAD_SKILLS_FILES:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as file:
                    data = json.load(file)
                    if "skills" in data:
                        merged_skills["skills"].update(data["skills"])
            except json.JSONDecodeError:
                logging.error(f"🚨 ERROR: Failed to parse {file_path}. Skipping.")

    return merged_skills

def load_toolstack():
    """Loads tools ONLY from orchestrate_tools.json (for execution)."""
    if not os.path.exists(ORCHESTRATE_TOOLS_PATH):
        logging.error(f"🚨 ERROR: {ORCHESTRATE_TOOLS_PATH} not found.")
        return {"tools": {}}

    try:
        with open(ORCHESTRATE_TOOLS_PATH, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        logging.error(f"🚨 ERROR: Failed to parse {ORCHESTRATE_TOOLS_PATH}.")
        return {"tools": {}}

def run_script(tool_name, action, params):
    """Runs a tool dynamically based on orchestrate_tools.json."""
    tools = load_toolstack().get("tools", {})

    logging.info(f"🚨 DEBUG: Loaded execution tools: {list(tools.keys())}")

    if tool_name not in tools:
        logging.error(f"🚨 ERROR: Tool '{tool_name}' not found in execution list.")
        return {"error": f"Tool '{tool_name}' not found."}

    script_path = tools[tool_name].get("path")

    if not script_path or not os.path.isfile(script_path):
        logging.error(f"🚨 ERROR: Script file does not exist at {script_path}.")
        return {"error": f"Script for '{tool_name}' not found."}

    params_json = json.dumps(params)

    try:
        result = subprocess.run(
            ["python3", script_path, action, "--params", params_json],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        return {"error": "Script execution failed", "details": e.stderr.strip()}

@app.post("/execute_task")
async def execute_task(request: Request):
    """Executes a tool action dynamically."""
    request_data = await request.json()
    logging.info(f"🚨 DEBUG: Incoming request: {request_data}")

    tool_name = request_data.get("tool_name")
    action = request_data.get("action")
    params = request_data.get("params", {})

    if not tool_name or not action:
        logging.error("🚨 ERROR: Missing tool_name or action in request")
        raise HTTPException(status_code=400, detail="Missing tool_name or action.")

    logging.info(f"🚨 DEBUG: Executing {tool_name} -> {action} with params: {params}")
    response = run_script(tool_name, action, params)
    if "error" in response:
        logging.error(f"🚨 ERROR: Execution failed: {response}")
        raise HTTPException(status_code=500, detail=response)
    
    return response
