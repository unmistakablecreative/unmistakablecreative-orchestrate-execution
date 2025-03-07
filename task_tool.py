import json
import os
import argparse

TASKS_FILE = "tasks.json"

def load_tasks():
    """Loads tasks from tasks.json."""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return {"tasks": []}

def save_tasks(data):
    """Saves updates to tasks.json."""
    with open(TASKS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def execute_action(action, params):
    """Executes task actions."""
    data = load_tasks()
    
    if action == "add_task":
        task = {"content": params.get("input", ""), "status": "pending"}
        data["tasks"].append(task)
        save_tasks(data)
        return {"status": "success", "message": "Task added successfully."}
    elif action == "list_tasks":
        return {"status": "success", "tasks": data["tasks"]}
    elif action == "update_task":
        task_index = params.get("options", {}).get("task_index")
        new_status = params.get("options", {}).get("status", "pending")
        if task_index is not None and 0 <= task_index < len(data["tasks"]):
            data["tasks"][task_index]["status"] = new_status
            save_tasks(data)
            return {"status": "success", "message": "Task updated successfully."}
        return {"status": "error", "message": "Invalid task index."}
    elif action == "batch_add":
        tasks = params.get("options", {}).get("tasks", [])
        for task in tasks:
            data["tasks"].append({"content": task, "status": "pending"})
        save_tasks(data)
        return {"status": "success", "message": "Batch tasks added successfully."}
    elif action == "batch_delete":
        task_indices = params.get("options", {}).get("task_indices", [])
        data["tasks"] = [task for i, task in enumerate(data["tasks"]) if i not in task_indices]
        save_tasks(data)
        return {"status": "success", "message": "Batch tasks deleted successfully."}
    else:
        return {"status": "error", "message": "Invalid action or missing parameters."}

def main():
    parser = argparse.ArgumentParser(description="Task Tool")
    parser.add_argument("action", help="Action to perform")
    parser.add_argument("--params", type=str, required=True, help="JSON-encoded parameters")
    args = parser.parse_args()
    
    try:
        params_dict = json.loads(args.params)
    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "Invalid JSON format."}, indent=4))
        return
    
    result = execute_action(args.action, params_dict)
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
