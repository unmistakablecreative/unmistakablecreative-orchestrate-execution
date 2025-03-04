import json
import os
import argparse
import logging

logging.basicConfig(level=logging.INFO)

WORKFLOW_PATH = os.path.join(os.getcwd(), "orchestrate_workflows.json")

def load_workflows():
    """Load the current orchestrate_workflows.json file."""
    if not os.path.exists(WORKFLOW_PATH):
        return {"workflows": {}}

    with open(WORKFLOW_PATH, "r") as file:
        return json.load(file)

def save_workflows(workflows):
    """Save updates to orchestrate_workflows.json."""
    with open(WORKFLOW_PATH, "w") as file:
        json.dump(workflows, file, indent=4)
    logging.info("Workflow data successfully updated.")

def get_supported_actions():
    """Return supported actions as a JSON dictionary."""
    return {
        "add_workflow": ["workflow_name", "workflow_config"],
        "modify_workflow": ["workflow_name", "new_steps", "replace"],
        "remove_workflow": ["workflow_name"],
        "search_workflow": ["query"]
    }

def search_workflow(query):
    """Search for a workflow matching a query."""
    workflows = load_workflows().get("workflows", {})
    results = {name: config for name, config in workflows.items() if query.lower() in name.lower()}
    
    return results if results else {"message": "No workflows found."}

def add_workflow(workflow_name, workflow_config):
    """Add a new workflow to orchestrate_workflows.json."""
    workflows = load_workflows()

    if "workflows" not in workflows:
        workflows["workflows"] = {}

    if workflow_name in workflows["workflows"]:
        return {"status": "error", "message": f"Workflow '{workflow_name}' already exists."}

    workflows["workflows"][workflow_name] = workflow_config
    save_workflows(workflows)

    return {"status": "success", "message": f"✅ Workflow '{workflow_name}' added successfully."}

def main():
    parser = argparse.ArgumentParser(description="Orchestrate Workflow Tool CLI")
    parser.add_argument("action", choices=["get_supported_actions", "search_workflow", "add_workflow"], help="Action to perform")
    parser.add_argument("--params", type=str, help="JSON-encoded parameters for the action")

    args = parser.parse_args()
    params = json.loads(args.params) if args.params else {}

    if args.action == "get_supported_actions":
        print(json.dumps(get_supported_actions(), indent=4))
        return

    if args.action == "search_workflow":
        result = search_workflow(params.get("query", ""))
    elif args.action == "add_workflow":
        if "workflow_name" not in params or "workflow_config" not in params:
            result = {"status": "error", "message": "❌ 'workflow_name' and 'workflow_config' are required for add_workflow."}
        else:
            result = add_workflow(params["workflow_name"], params["workflow_config"])
    else:
        result = {"status": "error", "message": "Invalid action"}

    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
