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
    ensure_task_file()
    with open(TASK_FILE, "r") as f:
        return json.load(f)

def write_tasks(data):
    """Write tasks to the task file."""
    with open(TASK_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_supported_actions():
    """Return structured JSON output for Orchestrate."""
    actions = {
        "create_task": ["content", "description", "project", "priority", "impact", "dependencies"],
        "update_task": ["task_id", "updates"],
        "delete_task": ["task_ids"],
        "list_tasks": ["sort_by"],
        "search_tasks": ["query"],
        "get_supported_actions": []
    }
    print(json.dumps(actions, indent=4))

def create_task(content, description=None, project=None, priority=None, impact=None, dependencies=None):
    """Add a new task with smart defaults and flexible input."""
    task_id = str(int(datetime.utcnow().timestamp()))
    new_task = {
        "task_id": task_id,
        "content": content,
        "description": description or content,
        "project": project or "General",
        "status": "pending",
        "priority": str(priority) if priority else "Normal",
        "impact": str(impact) if impact else "Standard",
        "dependencies": dependencies if isinstance(dependencies, list) else [],
        "execution_time_estimate": None,
        "last_touched": datetime.utcnow().isoformat()
    }
    data = read_tasks()
    data["tasks"].append(new_task)
    write_tasks(data)
    print(json.dumps({"status": "success", "message": f"Task '{content}' added.", "task_id": task_id}, indent=4))

def update_task(task_id, updates):
    """Update an existing task with improved handling."""
    data = read_tasks()
    for task in data["tasks"]:
        if task["task_id"] == task_id:
            for key, value in updates.items():
                if value is not None:
                    task[key] = str(value) if key in ["priority", "impact"] else value
            task["last_touched"] = datetime.utcnow().isoformat()
            write_tasks(data)
            print(json.dumps({"status": "success", "message": f"Task {task_id} updated."}, indent=4))
            return
    print(json.dumps({"status": "error", "message": "Task not found."}, indent=4))

def delete_task(task_ids):
    """Delete one or multiple tasks, improving flexibility."""
    if isinstance(task_ids, str):
        task_ids = [task_ids]  # Convert single ID to a list

    data = read_tasks()
    tasks_before = len(data["tasks"])
    data["tasks"] = [task for task in data["tasks"] if task["task_id"] not in task_ids]

    deleted_count = tasks_before - len(data["tasks"])
    if deleted_count == 0:
        print(json.dumps({"status": "error", "message": "No matching tasks found."}, indent=4))
        return

    write_tasks(data)
    print(json.dumps({"status": "success", "message": f"Deleted {deleted_count} tasks."}, indent=4))

def list_tasks(sort_by=None):
    """List tasks with optional sorting and smart defaults."""
    tasks = read_tasks()["tasks"]

    if sort_by in ["priority", "impact"]:
        tasks.sort(key=lambda t: str(t.get(sort_by, "")), reverse=True)

    print(json.dumps({"status": "success", "tasks": tasks}, indent=4))

def search_tasks(query=None):
    """Search for tasks with more flexible matching."""
    if not query:
        print(json.dumps({"status": "error", "message": "Search query is required."}, indent=4))
        return

    results = [
        task for task in read_tasks()["tasks"]
        if query.lower() in task["content"].lower()
        or query.lower() in task.get("project", "").lower()
        or query.lower() in str(task.get("priority", "")).lower()
    ]
    print(json.dumps({"status": "success", "tasks": results}, indent=4))

def main():
    """Command-line execution for Task Tool."""
    parser = argparse.ArgumentParser(description="Orchestrate Tasks Tool CLI")
    parser.add_argument("action", type=str, help="Action to perform")
    parser.add_argument("--params", type=str, help="JSON string of parameters", default="{}")

    args = parser.parse_args()

    try:
        params = json.loads(args.params) if args.params else {}
    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "Invalid JSON format."}, indent=4))
        return

    actions = {
        "create_task": create_task,
        "update_task": update_task,
        "delete_task": delete_task,
        "list_tasks": list_tasks,
        "search_tasks": search_tasks,
        "get_supported_actions": get_supported_actions
    }

    if args.action not in actions:
        print(json.dumps({"status": "error", "message": f"Invalid action: {args.action}."}, indent=4))
        return

    actions[args.action](**{k: v for k, v in params.items() if v is not None})

if __name__ == "__main__":
    main()
