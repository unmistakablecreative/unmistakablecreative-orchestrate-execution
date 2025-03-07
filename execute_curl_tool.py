import subprocess
import json
import argparse

def execute_curl(command):
    """Executes a curl command and returns the response."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Execute a curl command.")
    parser.add_argument("--command", type=str, required=True, help="The full curl command to execute.")
    args = parser.parse_args()
    
    result = execute_curl(args.command)
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
