import os
import logging
import subprocess
import json
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class PodcastCoverTool:
    def __init__(self, config=None):
        """
        Initializes the Podcast Cover Tool.
        """
        self.config = config or {}
        self.background_script_path = "/Users/srinivas/Orchestrate Github/orchestrate-execution/Podcast Workflow/UCBackground_dev.sh"
        self.jsx_file_path = "/Users/srinivas/Orchestrate Github/orchestrate-execution/Podcast Workflow/CovergenWithActions.jsx"
        self.assets_path = "/Users/srinivas/Library/CloudStorage/Dropbox/2. Areas of Responsibility/Unmistkable Creative/1.Podcast/Covers/Assets/"
        self.finished_covers_path = "/Users/srinivas/Library/CloudStorage/Dropbox/2. Areas of Responsibility/Unmistkable Creative/1.Podcast/Covers/Finished Covers/"
        self.dropbox_root_path = "/2. Areas of Responsibility/Unmistkable Creative/1.Podcast/Covers/Finished Covers/"  # Relative to Dropbox root

    def get_supported_actions(self):
        """
        Returns the list of supported actions.
        """
        return {
            "create_cover": ["guest_name", "episode_title", "custom_prompt"]
        }

    def execute(self, action, params):
        """
        Executes the podcast cover creation process.
        """
        if action == "get_supported_actions":
            return self.get_supported_actions()

        if action != "create_cover":
            raise ValueError(f"Unsupported action: {action}")

        guest_name = params.get("guest_name")
        episode_title = params.get("episode_title")
        custom_prompt = params.get("custom_prompt")

        if not guest_name or not episode_title:
            raise ValueError("'guest_name' and 'episode_title' are required.")

        logging.info(f"Generating podcast cover for guest: {guest_name}, title: {episode_title}")

        # Step 1: Generate Background
        background_path = self.generate_background(guest_name, episode_title, custom_prompt)
        if not os.path.exists(background_path):
            raise FileNotFoundError(f"Background image not found: {background_path}")

        # Step 2: Run Photoshop JSX Script
        self.run_photoshop_jsx(guest_name)

        # Step 3: Generate Temporary Link for Finished Cover
        formatted_guest_name = guest_name.lower().replace(" ", "-")
        local_cover_path = os.path.join(self.finished_covers_path, f"{formatted_guest_name}-cover.jpg")
        dropbox_relative_path = os.path.join(self.dropbox_root_path, f"{formatted_guest_name}-cover.jpg")

        if not os.path.exists(local_cover_path):
            raise FileNotFoundError(f"Finished cover not found: {local_cover_path}")

        # Generate the temporary link using the relative Dropbox path
        markdown_link = self.generate_temporary_link(dropbox_relative_path, formatted_guest_name)

        return {
            "status": "success",
            "message": "Podcast cover created successfully.",
            "cover_markdown": markdown_link,
        }

    def get_default_prompt(self, guest_name, episode_title):
        """
        Generates a default background prompt dynamically.
        """
        return (
            f"A visually captivating background for a podcast titled '{episode_title}'. "
            f"The guest name '{guest_name}' should appear in sleek, modern text beneath the title. "
            "Place the title in the top right corner using a bold, handwritten font. Use bright, abstract colors to convey positivity and growth."
        )

    def generate_background(self, guest_name, episode_title, custom_prompt):
        """
        Generates the podcast background by running the background script.
        """
        formatted_guest_name = guest_name.lower().replace(" ", "-")
        formatted_title = episode_title.replace('"', '\\"')

        prompt = custom_prompt if custom_prompt else self.get_default_prompt(guest_name, episode_title)
        logging.info(f"Using prompt: {prompt}")

        command = ["/bin/bash", self.background_script_path, formatted_guest_name, formatted_title, prompt]
        logging.info(f"Running background script: {command}")

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Background script failed: {result.stderr}")

        logging.info(f"Background script output: {result.stdout}")
        return os.path.join(self.assets_path, f"{formatted_guest_name}-bg.jpg")

    def run_photoshop_jsx(self, guest_name):
        """
        Executes the Photoshop JSX script to generate the final podcast cover.
        """
        formatted_guest_name = guest_name.lower().replace(" ", "-")
        command = [
            "osascript",
            "-e",
            f'tell application "Adobe Photoshop 2025" to do javascript file "{self.jsx_file_path}" with arguments "{formatted_guest_name}"'
        ]

        logging.info(f"Running Photoshop JSX script: {command}")
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Photoshop JSX script failed: {result.stderr}")

        logging.info(f"Photoshop script output: {result.stdout}")

    def generate_temporary_link(self, relative_path, formatted_guest_name):
        """
        Generates a temporary Dropbox link for the final podcast cover.
        """
        skillstack_path = "/Users/srinirao/Orchestrate-GitHub/sandbox-abstraction/skillstack.json"
        if not os.path.exists(skillstack_path):
            raise FileNotFoundError(f"Skillstack file not found: {skillstack_path}")

        with open(skillstack_path, "r") as file:
            skillstack = json.load(file)
        
        api_key = skillstack.get("tools", {}).get("dropbox_tool", {}).get("config", {}).get("api_key")
        if not api_key:
            raise ValueError("Dropbox API key not found in skillstack.")

        url = "https://api.dropboxapi.com/2/files/get_temporary_link"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {"path": relative_path}

        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to generate Dropbox link: {response.text}")

        temporary_link = response.json().get("link")
        markdown_link = f"![Podcast Cover for {formatted_guest_name}]({temporary_link})"
        logging.info(f"Generated Markdown Link: {markdown_link}")
        return markdown_link
