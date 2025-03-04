import os
import json
import sys
import subprocess
import shlex
from fastapi import FastAPI, HTTPException, Request

# Set paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLSTACK_PATH = os.path.join(BASE_DIR, "orchestrate_tools.json")

# FastAPI app
app = FastAPI()

# Define tools that expect JSON-style `--params`
JSON_TOOLS = {"ideogram_tool", "task_tool", "dropbox_tool"}

class OrchestrateServer:
    def __init__(self):
        if not os.path.isfile(TOOLSTACK_PATH):
            raise FileNotFoundError(f"Toolstack file not found at '{TOOLSTACK_PATH}'")
        self.tools = self.load_toolstack()

    def load_toolstack(self):
        """Loads the toolstack and ensures tools are properly structured."""
        try:
            with open(TOOLSTACK_PATH, "r") as f:
                toolstack = json.load(f)
            if "tools" not in toolstack:
                raise ValueError("Toolstack file is missing the 'tools' key.")
            print(f"✅ Loaded toolstack from '{TOOLSTACK_PATH}'")
            return toolstack["tools"]
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse toolstack: {e}")

    def get_tool_path(self, tool_name):
        """Retrieve tool script path from orchestrate_tools.json"""
        return self.tools.get(tool_name, {}).get("path")

    def get_supported_actions(self, tool_name, script_path):
        """Fetches supported actions from the tool"""
        try:
            result = subprocess.run(
                [sys.executable, script_path, "get_supported_actions"],
                capture_output=True, text=True, check=True
            )
            actions = json.loads(result.stdout.strip())
            if not isinstance(actions, dict):
                return {}
            return actions
        except Exception:
            return {}  # Instead of error, return empty dict (fails cleanly)

server = OrchestrateServer()

@app.get("/load_toolstack")
async def load_toolstack():
    """Returns the toolstack configuration to ensure the API structure is correct."""
    try:
        return {"status": "success", "tools": server.tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load toolstack: {e}")

@app.post("/execute_task")
async def execute_task(request: Request):
    """Dynamically executes tools as Python scripts via API"""
    try:
        body = await request.json()
        tool_name = body.get("tool_name")
        action = body.get("action")
        params = body.get("params", {})

        if not tool_name or not action:
            raise HTTPException(status_code=400, detail="Missing 'tool_name' or 'action'.")

        # ✅ Step 1: Ensure the tool exists
        script_path = server.get_tool_path(tool_name)
        if not script_path:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found in orchestrate_tools.json.")
        if not os.path.isfile(script_path):
            raise HTTPException(status_code=404, detail=f"Tool script '{script_path}' does not exist on disk.")

        # ✅ Step 2: Fetch supported actions
        supported_actions = server.get_supported_actions(tool_name, script_path)
        if not supported_actions:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve supported actions for '{tool_name}'.")

        if action not in supported_actions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action: '{action}'. Supported actions: {list(supported_actions.keys())}"
            )

        # ✅ Step 3: Validate parameters
        expected_params = set(supported_actions[action])
        received_params = set(params.keys())

        if not received_params.issubset(expected_params):
            invalid_params = received_params - expected_params
            raise HTTPException(
                status_code=400,
                detail=f"Invalid parameters: {invalid_params}. Expected: {expected_params}"
            )

        if expected_params and not received_params:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required parameters. Expected: {expected_params}"
            )

        # ✅ Step 4: Handle API key only for Ideogram Tool
        env = os.environ.copy()
        if tool_name == "ideogram_tool":
            api_key = params.pop("api_key", None)
            if not api_key:
                raise HTTPException(status_code=500, detail="❌ Missing IDEOGRAM_API_KEY in request parameters.")
            env["IDEOGRAM_API_KEY"] = api_key  # Pass it explicitly

        # ✅ Step 5: Construct command based on tool execution mode
        if tool_name in JSON_TOOLS:
            params_json = json.dumps(params)
            escaped_params = shlex.quote(params_json)
            command = f"{sys.executable} {shlex.quote(script_path)} {action} --params {escaped_params}"
        else:
            cli_params = [f"--{key}={shlex.quote(str(value))}" for key, value in params.items()]
            command = f"{sys.executable} {shlex.quote(script_path)} {action} " + " ".join(cli_params)

        # ✅ Step 6: Execute the tool
        result = subprocess.run(command, shell=True, capture_output=True, text=True, env=env)
        response = result.stdout.strip() or result.stderr.strip() or "No output from tool."

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Tool execution failed: {response}")

        return {"status": "success", "result": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing task: {e}")
