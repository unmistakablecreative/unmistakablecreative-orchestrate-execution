import argparse
import requests
import json
import os
import sys

# Mailjet API base URL
BASE_URL = "https://api.mailjet.com/v3.1"

def send_email(api_key, secret_key, from_email, from_name, to_email, to_name, subject, text_part, html_part):
    """Send an email using Mailjet."""
    url = f"{BASE_URL}/send"
    data = {
        "Messages": [
            {
                "From": {"Email": from_email, "Name": from_name},
                "To": [{"Email": to_email, "Name": to_name}],
                "Subject": subject,
                "TextPart": text_part,
                "HTMLPart": html_part
            }
        ]
    }
    return _send_request("POST", url, api_key, secret_key, data)

def check_status(api_key, secret_key, message_id):
    """Check the status of an email message."""
    url = f"https://api.mailjet.com/v3/REST/message/{message_id}"
    return _send_request("GET", url, api_key, secret_key)

def add_contact(api_key, secret_key, email, name, list_id):
    """Add a contact to a Mailjet list."""
    url = "https://api.mailjet.com/v3/REST/contact"
    data = {"Email": email, "Name": name, "IsExcludedFromCampaigns": "false"}
    
    response = _send_request("POST", url, api_key, secret_key, data)
    
    # Now associate the contact with the list
    list_url = f"https://api.mailjet.com/v3/REST/contactslist/{list_id}/managemanycontacts"
    list_data = {
        "Action": "addnoforce",
        "Contacts": [{"Email": email}]
    }
    return _send_request("POST", list_url, api_key, secret_key, list_data)

def get_contacts(api_key, secret_key, list_id):
    """Retrieve contacts from a specific list."""
    url = f"https://api.mailjet.com/v3/REST/contactslist/{list_id}/managemanycontacts"
    return _send_request("GET", url, api_key, secret_key)

def remove_contact(api_key, secret_key, email, list_id):
    """Remove a contact from a Mailjet list."""
    url = "https://api.mailjet.com/v3/REST/contact/managemanycontacts"
    data = {
        "Action": "remove",
        "Contacts": [{"Email": email}]
    }
    return _send_request("POST", url, api_key, secret_key, data)

def _send_request(method, url, api_key, secret_key, data=None):
    """Handles sending API requests to Mailjet with improved error handling."""
    try:
        response = requests.request(
            method,
            url,
            auth=(api_key, secret_key),
            json=data if data else None
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {"error": "HTTP error occurred", "message": str(http_err), "status_code": response.status_code}
    except requests.exceptions.ConnectionError:
        return {"error": "Network connection error", "message": "Could not connect to Mailjet API"}
    except requests.exceptions.Timeout:
        return {"error": "Request timeout", "message": "Mailjet API took too long to respond"}
    except requests.exceptions.RequestException as err:
        return {"error": "Request failed", "message": str(err)}

def get_supported_actions():
    """Returns the list of supported actions and their parameters."""
    return json.dumps({
        "send_email": ["from_email", "from_name", "to_email", "to_name", "subject", "text_part", "html_part"],
        "check_status": ["message_id"],
        "add_contact": ["email", "name", "list_id"],
        "get_contacts": ["list_id"],
        "remove_contact": ["email", "list_id"]
    }, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mailjet Email and Contact Management Tool")

    parser.add_argument("action", help="Action to perform", choices=[
        "send_email", "check_status", "add_contact", "get_contacts", "remove_contact", "get_supported_actions"
    ])
    
    parser.add_argument("params", nargs="*", help="Parameters for the selected action")

    args = parser.parse_args()

    # Secure API key validation
    api_key = os.getenv("MAILJET_API_KEY", None)
    secret_key = os.getenv("MAILJET_SECRET_KEY", None)

    if not api_key or not secret_key:
        print(json.dumps({"error": "Missing API credentials", "message": "MAILJET_API_KEY and MAILJET_SECRET_KEY are required"}))
        sys.exit(1)

    try:
        if args.action == "send_email":
            if len(args.params) != 7:
                raise ValueError("Usage: send_email <from_email> <from_name> <to_email> <to_name> <subject> <text_part> <html_part>")
            result = send_email(api_key, secret_key, *args.params)

        elif args.action == "check_status":
            if len(args.params) != 1:
                raise ValueError("Usage: check_status <message_id>")
            result = check_status(api_key, secret_key, args.params[0])

        elif args.action == "add_contact":
            if len(args.params) != 3:
                raise ValueError("Usage: add_contact <email> <name> <list_id>")
            result = add_contact(api_key, secret_key, *args.params)

        elif args.action == "get_contacts":
            if len(args.params) != 1:
                raise ValueError("Usage: get_contacts <list_id>")
            result = get_contacts(api_key, secret_key, args.params[0])

        elif args.action == "remove_contact":
            if len(args.params) != 2:
                raise ValueError("Usage: remove_contact <email> <list_id>")
            result = remove_contact(api_key, secret_key, *args.params)

        elif args.action == "get_supported_actions":
            result = get_supported_actions()

        else:
            raise ValueError("Invalid action specified.")

        print(json.dumps(result, indent=4))

    except ValueError as ve:
        print(json.dumps({"error": "Invalid parameters", "message": str(ve)}))
        sys.exit(1)
