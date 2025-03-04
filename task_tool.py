import json
import argparse
import os
from datetime import datetime

TASK_FILE = "orchestrate_tasks.json"

def ensure_task_file():
    """Ensure the task file exists."""
    if not os.path.exists(TASK_FILE):
        with open(TASK_FILE, "w") as f:
            json.dump({"tasks": []}, f)

def read_tasks():
    """Read tasks from the task file."""
    with open(TASK_FILE, "r") as f:
        return json.load(f)

def write_tasks(data):
    """Write tasks to the task file."""
    with open(TASK_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_supported_actions():
    """Return supported actions and required parameters."""
    return {
        "add_task": ["content", "description", "project", "priority", "impact"],
        "update_task": ["task_id", "updates"],
        "delete_task": ["task_id"],
        "list_tasks": ["status", "project", "priority"],
        "get_supported_actions": []
    }

def add_task(content, description=None, project=None, priority=None, impact=None):
    """Add a new task."""
    ensure_task_file()
    task_id = str(int(datetime.utcnow().timestamp()))
    new_task = {
        "task_id": task_id,
        "content": content,
        "description": description or "",
        "project": project or "",
        "status": "pending",
        "priority": priority or "",
        "impact": impact or "",
        "execution_time_estimate": None,
        "last_touched": datetime.utcnow().isoformat()
    }
    data = read_tasks()
    data["tasks"].append(new_task)
    write_tasks(data)
    print(json.dumps({"status": "success", "message": f"Task '{content}' added.", "task_id": task_id}, indent=4))

def update_task(task_id, updates):
    """Update an existing task."""
    ensure_task_file()
    data = read_tasks()
    for task in data["tasks"]:
        if task["task_id"] == task_id:
            task.update(updates)
            task["last_touched"] = datetime.utcnow().isoformat()
            write_tasks(data)
            print(json.dumps({"status": "success", "message": f"Task {task_id} updated."}, indent=4))
            return
    print(json.dumps({"status": "error", "message": "Task not found."}, indent=4))

def delete_task(task_id):
    """Delete a task."""
    ensure_task_file()
    data = read_tasks()
    tasks_before = len(data["tasks"])
    data["tasks"] = [task for task in data["tasks"] if task["task_id"] != task_id]
    
    if len(data["tasks"]) == tasks_before:
        print(json.dumps({"status": "error", "message": f"Task {task_id} not found."}, indent=4))
        return

    write_tasks(data)
    print(json.dumps({"status": "success", "message": f"Task {task_id} deleted."}, indent=4))

def list_tasks(status=None, project=None, priority=None):
    """List tasks with optional filters."""
    ensure_task_file()
    tasks = read_tasks()["tasks"]

    if status:
        tasks = [t for t in tasks if t["status"] == status]
    if project:
        tasks = [t for t in tasks if t["project"] == project]
    if priority:
        tasks = [t for t in tasks if str(t["priority"]) == str(priority)]

    print(json.dumps({"status": "success", "tasks": tasks}, indent=4))

def main():
    """Command-line execution for Task Tool."""
    parser = argparse.ArgumentParser(description="Orchestrate Tasks Tool CLI")
    parser.add_argument("action", type=str, help="Action to perform")
    parser.add_argument("--params", type=str, help="JSON string of parameters", default="{}")

    args = parser.parse_args()

    # Ensure valid JSON input
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "Invalid JSON format."}, indent=4))
        return

    # Fetch supported actions dynamically
    supported_actions_data = get_supported_actions()

    supported_actions = {
        "add_task": add_task,
        "update_task": update_task,
        "delete_task": delete_task,
        "list_tasks": list_tasks,
        "get_supported_actions": lambda: print(json.dumps(supported_actions_data, indent=4))
    }

    if args.action not in supported_actions:
        print(json.dumps({"status": "error", "message": f"Invalid action: {args.action}."}, indent=4))
        return

    # Execute the action
    action_params = {}
    required_params = supported_actions_data.get(args.action, [])

    for param in required_params:
        if param in params:
            action_params[param] = params[param]
        else:
            action_params[param] = None

    supported_actions[args.action](**action_params)

if __name__ == "__main__":
    main()
