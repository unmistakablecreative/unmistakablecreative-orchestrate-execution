import json
import os
import time
import subprocess
import logging

# Paths
QUEUE_FILE = "orchestrate_queue.json"
STATUS_FILE = "queue_status.json"
CHECK_INTERVAL = 5  # Check the queue every 5 seconds

# Logging setup
logging.basicConfig(filename="autonomy.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_queue():
    """Load the task queue from JSON."""
    if not os.path.exists(QUEUE_FILE):
        return []

    with open(QUEUE_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            logging.error("❌ Invalid JSON format in queue file.")
            return []

def save_status(task_id, status, result=None, message=None):
    """Update queue_status.json with task execution results."""
    status_data = {"tasks": []}

    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            try:
                status_data = json.load(f)
            except json.JSONDecodeError:
                logging.error("❌ Invalid JSON in queue_status.json. Resetting file.")

    # Update or add new task status
    updated = False
    for task in status_data["tasks"]:
        if task["task_id"] == task_id:
            task["status"] = status
            if result:
                task["result"] = result
            if message:
                task["message"] = message
            updated = True

    if not updated:
        status_data["tasks"].append({
            "task_id": task_id,
            "status": status,
            "result": result,
            "message": message
        })

    with open(STATUS_FILE, "w") as f:
        json.dump(status_data, f, indent=4)

def execute_task(task):
    """Execute the task using the appropriate Python script and update status."""
    action = task.get("action")
    params = task.get("params", {})

    save_status(action, "In Progress", message=f"Executing {action}...")

    script_path = f"{action}.py"
    params_json = json.dumps(params)

    try:
        logging.info(f"🚀 Executing: {script_path} {action} --params '{params_json}'")
        subprocess.run(["python3", script_path, action, "--params", params_json], check=True)
        save_status(action, "Completed", result=f"Task '{action}' executed successfully.", message=f"✅ {action} is done!")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Task execution failed: {e}")
        save_status(action, "Failed", message=f"❌ {action} failed to execute.")

def process_queue():
    """Continuously checks the queue and processes tasks."""
    while True:
        queue = load_queue()
        if queue:
            logging.info(f"📌 {len(queue)} tasks found in queue. Processing...")
            for task in queue:
                execute_task(task)

            # Clear queue after execution
            with open(QUEUE_FILE, "w") as f:
                json.dump([], f)
            logging.info("✅ Task queue cleared after execution.")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    logging.info("🔥 Autonomy script started. Watching for tasks...")
    process_queue()
