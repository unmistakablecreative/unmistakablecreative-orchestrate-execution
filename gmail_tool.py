import argparse
import json
import os
import base64
import requests
from dotenv import load_dotenv  # <-- Load environment variables
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Load environment variables from .env file
load_dotenv()

# Load Gmail account credentials
GMAIL_ACCOUNTS = {
    "srini@unmistakablemedia.com": {
        "access_token": os.getenv("GMAIL_ACCESS_TOKEN_WORK"),
        "refresh_token": os.getenv("GMAIL_REFRESH_TOKEN_WORK"),
        "client_id": os.getenv("GMAIL_CLIENT_ID_WORK"),
        "client_secret": os.getenv("GMAIL_CLIENT_SECRET_WORK"),
        "token_uri": os.getenv("GMAIL_TOKEN_URI", "https://oauth2.googleapis.com/token"),
    },
}

class GmailTool:
    def __init__(self, account):
        self.account = account
        self.creds = self.get_credentials(account)
        self.service = build("gmail", "v1", credentials=self.creds)

    def get_credentials(self, account):
        """Retrieve and refresh credentials if expired."""
        if account not in GMAIL_ACCOUNTS:
            raise ValueError(f"No credentials found for account: {account}")

        account_config = GMAIL_ACCOUNTS[account]
        
        # Validate all required OAuth fields
        missing_keys = [key for key in ["access_token", "refresh_token", "client_id", "client_secret", "token_uri"]
                        if not account_config.get(key)]
        if missing_keys:
            raise ValueError(f"Missing required OAuth fields: {', '.join(missing_keys)}")

        creds = Credentials(
            token=account_config["access_token"],
            refresh_token=account_config["refresh_token"],
            client_id=account_config["client_id"],
            client_secret=account_config["client_secret"],
            token_uri=account_config["token_uri"]
        )
        
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        return creds

    def fetch_emails(self, timeframe="1d", max_results=10, query=None):
        """Fetches full email details including subject, sender, and body content."""
        query = query or f"newer_than:{timeframe}"
        response = self.service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = response.get("messages", [])

        if not messages:
            return {"status": "success", "emails": []}

        email_data = []
        for message in messages:
            msg_detail = self.service.users().messages().get(userId="me", id=message["id"]).execute()
            headers = msg_detail.get("payload", {}).get("headers", [])
            body = self.get_clean_email_body(msg_detail)

            email_data.append({
                "id": message["id"],
                "subject": self.get_header(headers, "Subject"),
                "sender": self.get_header(headers, "From"),
                "body": body
            })

        return {"status": "success", "emails": email_data}

    def get_clean_email_body(self, msg_detail):
        """Extracts and decodes email body properly handling text and HTML."""
        try:
            payload = msg_detail.get("payload", {})
            parts = payload.get("parts", [])

            body_data = ""
            mime_type = ""
            if not parts:
                body_data = payload.get("body", {}).get("data", "")
                mime_type = payload.get("mimeType", "")
            else:
                for part in parts:
                    if part.get("mimeType") == "text/plain":
                        body_data = part.get("body", {}).get("data", "")
                        mime_type = "text/plain"
                        break
                    elif part.get("mimeType") == "text/html":
                        body_data = part.get("body", {}).get("data", "")
                        mime_type = "text/html"

            decoded_body = base64.urlsafe_b64decode(body_data).decode("utf-8") if body_data else ""
            if mime_type == "text/html":
                soup = BeautifulSoup(decoded_body, "html.parser")
                return soup.get_text(separator=" ").strip()
            return decoded_body.strip() if decoded_body else "No body content"
        except Exception:
            return "Failed to fetch email body"

    def get_header(self, headers, header_name):
        """Extracts the specified header value from the email headers."""
        for header in headers:
            if header["name"].lower() == header_name.lower():
                return header["value"]
        return "Unknown"

def get_supported_actions():
    """Returns the list of supported actions and required parameters."""
    return {
        "fetch_emails": ["account", "timeframe", "max_results", "query"]
    }

def main():
    parser = argparse.ArgumentParser(description="Gmail Fetch Tool")
    parser.add_argument("action", choices=["fetch_emails", "get_supported_actions"])
    parser.add_argument("--params", type=str, help="JSON-encoded parameters for the action")

    args = parser.parse_args()
    
    if args.action == "get_supported_actions":
        print(json.dumps(get_supported_actions(), indent=4))
        return

    params = json.loads(args.params) if args.params else {}

    tool = GmailTool(params["account"])

    if args.action == "fetch_emails":
        result = tool.fetch_emails(params.get("timeframe", "1d"), params.get("max_results", 10), params.get("query"))
        print(json.dumps(result, indent=4))
    else:
        print(json.dumps({"status": "error", "message": "Invalid action"}))

if __name__ == "__main__":
    main()
