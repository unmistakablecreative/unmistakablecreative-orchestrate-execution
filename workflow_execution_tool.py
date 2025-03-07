import json
import os
import argparse
import subprocess

def load_workflow(workflow_name):
    """Loads the workflow definition from orchestrate_workflows.json."""
    workflow_file = "orchestrate_workflows.json"
    if not os.path.exists(workflow_file):
        return {"status": "error", "message": "Workflow file not found."}
    
    with open(workflow_file, "r") as f:
        workflows = json.load(f)
    
    return workflows.get("workflows", {}).get(workflow_name, {"status": "error", "message": "Workflow not found."})

def execute_step(step, previous_output):
    """Executes a single step in the workflow, safely replacing placeholders."""
    tool = step.get("tool")
    action = step.get("action")
    params = step.get("params", {})
    
    previous_output_str = json.dumps(previous_output) if isinstance(previous_output, (dict, list)) else str(previous_output)
    
    def replace_placeholders(obj):
        if isinstance(obj, dict):
            return {k: replace_placeholders(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_placeholders(v) for v in obj]
        elif isinstance(obj, str):
            return obj.replace("{input}", previous_output_str).replace("{previous_output}", previous_output_str)
        return obj
    
    params = replace_placeholders(params)
    
    if tool == "no_tool_required":
        return {"status": "success", "message": "Step completed by AI.", "output": previous_output}
    
    if not tool or not action:
        return {"status": "error", "message": "Invalid step definition."}
    
    command = ["python3", tool + ".py", action, "--params", json.dumps(params)]
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        return {"status": "error", "message": result.stderr}

def execute_workflow(params):
    """Executes a full workflow from orchestrate_workflows.json."""
    workflow_name = params.get("workflow_name")
    workflow_input = params.get("workflow_input")
    
    if not workflow_name or not workflow_input:
        return {"status": "error", "message": "Missing workflow_name or workflow_input in params."}
    
    workflow = load_workflow(workflow_name)
    
    if "status" in workflow and workflow["status"] == "error":
        return workflow
    
    output = workflow_input
    for step in workflow.get("steps", []):
        step_result = execute_step(step, output)
        if step_result.get("status") == "error":
            return step_result
        output = step_result
    
    return output

def main():
    parser = argparse.ArgumentParser(description="Workflow Execution Tool")
    parser.add_argument("action", choices=["execute_workflow"], help="The action to perform")
    parser.add_argument("--params", type=str, required=True, help="JSON string containing parameters")
    args = parser.parse_args()
    
    try:
        params_dict = json.loads(args.params.replace("'", '"'))
    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "Invalid JSON format in --params."}, indent=4))
        return
    
    result = execute_workflow(params_dict)
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
