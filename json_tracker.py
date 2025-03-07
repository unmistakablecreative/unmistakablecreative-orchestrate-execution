import json
import sys

def update_field(json_file, identifier, field, new_value):
    """Update a specific field in a JSON file based on an identifier."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated = False
    for entry in data:
        if identifier in entry.values():  # Check if identifier exists in any field
            entry[field] = new_value  # Update the specified field
            updated = True
            break  # Stop after the first match

    if updated:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"✅ Updated '{field}' to '{new_value}' for '{identifier}' in {json_file}")
    else:
        print(f"❌ No entry found with identifier '{identifier}' in {json_file}")

# Run from CLI: python json_tracker.py <json_file> update_field <identifier> <field> <new_value>
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python json_tracker.py <json_file> update_field <identifier> <field> <new_value>")
        sys.exit(1)

    _, json_file, action, identifier, field, new_value = sys.argv

    if action == "update_field":
        update_field(json_file, identifier, field, new_value)
    else:
        print("❌ Unsupported action. Use 'update_field'.")
