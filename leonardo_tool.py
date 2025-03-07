import requests
import json
import argparse
import time

CREDENTIALS_FILE = "credentials.json"
BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"

def load_api_key():
    """Loads Leonardo API key from credentials.json."""
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            creds = json.load(f)
        return creds.get("leonardo_api_key")
    return None

def generate_image(api_key, prompt, width=1024, height=768, num_images=1, preset_style="DYNAMIC", model_id="b24e16ff-06e3-43eb-8d33-4416c2d75876"):
    """Generates images using Leonardo AI."""
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json", "Content-Type": "application/json"}
    payload = {
        "alchemy": True,
        "height": height,
        "width": width,
        "num_images": num_images,
        "presetStyle": preset_style,
        "modelId": model_id,
        "prompt": prompt
    }
    
    response = requests.post(f"{BASE_URL}/generations", headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        generation_id = data.get("generationId")
        if generation_id:
            return fetch_generated_image(api_key, generation_id)
        return {"status": "error", "message": "Failed to retrieve generation ID."}
    return {"status": "error", "message": f"Request failed: {response.status_code}", "details": response.text}

def fetch_generated_image(api_key, generation_id):
    """Fetches a previously generated image using its generation ID."""
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    url = f"{BASE_URL}/generations/{generation_id}"
    
    for _ in range(10):  # Retry up to 10 times
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            images = data.get("generatedImages", [])
            if images:
                return {"status": "success", "images": [img["url"] for img in images]}
        time.sleep(3)  # Wait before retrying
    
    return {"status": "error", "message": "Image generation timed out."}

def main():
    parser = argparse.ArgumentParser(description="Leonardo AI Tool")
    parser.add_argument("action", choices=["generate_image", "fetch_generated_image"], help="Action to perform")
    parser.add_argument("--params", type=str, required=True, help="JSON-encoded parameters")
    args = parser.parse_args()
    
    api_key = load_api_key()
    if not api_key:
        print(json.dumps({"status": "error", "message": "Leonardo API key is required in credentials.json."}, indent=2))
        return
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "Invalid JSON format."}, indent=2))
        return
    
    if args.action == "generate_image":
        result = generate_image(api_key, **params)
    elif args.action == "fetch_generated_image":
        result = fetch_generated_image(api_key, params.get("generation_id"))
    else:
        result = {"status": "error", "message": "Invalid action"}
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
