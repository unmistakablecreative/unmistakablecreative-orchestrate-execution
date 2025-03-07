import argparse
import json
import os
import requests
from dotenv import load_dotenv  # Load API key from .env

# Load environment variables
load_dotenv()

IDEOGRAM_URL = "https://api.ideogram.ai/generate"

def get_supported_actions():
    """Returns the supported actions and their required parameters."""
    return {
        "generate_image": ["input", "options"]
    }

def generate_image(input, options={}):
    """Executes the 'generate_image' action with simplified parameters."""
    
    api_key = os.getenv("IDEOGRAM_API_KEY")
    if not api_key:
        print(json.dumps({"status": "error", "message": "❌ Missing IDEOGRAM_API_KEY. Set it as an environment variable."}))
        return

    # ✅ Extract options with defaults
    aspect_ratio = options.get("aspect_ratio", "ASPECT_10_16")
    model = options.get("model", "V_2")
    magic_prompt_option = options.get("magic_prompt_option", "AUTO")

    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "image_request": {
            "prompt": input,
            "aspect_ratio": aspect_ratio,
            "model": model,
            "magic_prompt_option": magic_prompt_option
        }
    }

    response = requests.post(IDEOGRAM_URL, headers=headers, json=payload)

    if response.status_code == 200:
        print(json.dumps(response.json(), indent=4))
    else:
        print(json.dumps({"status": "error", "message": f"API request failed: {response.text}"}, indent=4))

def main():
    parser = argparse.ArgumentParser(description="Ideogram Tool Execution")
    parser.add_argument("action", choices=["generate_image", "get_supported_actions"], help="The action to perform")
    parser.add_argument("--params", type=str, required=True, help="JSON string containing parameters")

    args = parser.parse_args()

    # ✅ Ensure JSON input is valid
    try:
        params_dict = json.loads(args.params.replace("'", '"'))  # Fix single-quote JSON errors
    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "Invalid JSON format in --params."}, indent=4))
        return

    if args.action == "get_supported_actions":
        print(json.dumps(get_supported_actions(), indent=4))
        return

    actions = get_supported_actions()

    if args.action not in actions:
        print(json.dumps({"status": "error", "message": f"Invalid action: {args.action}"}))
        return

    # ✅ Call the function dynamically with named arguments
    globals()[args.action](params_dict["input"], params_dict.get("options", {}))

if __name__ == "__main__":
    main()
