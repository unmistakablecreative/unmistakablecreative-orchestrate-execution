import json
import sys

def update_json_field(json_file, old_field, new_field):
    """Rename a field in a JSON file."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)  # Load the JSON file

    for entry in data:
        if old_field in entry:  # Check if the field exists
            entry[new_field] = entry.pop(old_field)  # Rename the field

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)  # Save the updated JSON

    print(f"✅ Successfully updated '{old_field}' to '{new_field}' in {json_file}")

# Run from CLI: python update_json_field.py <json_file> <old_field> <new_field>
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python update_json_field.py <json_file> <old_field> <new_field>")
        sys.exit(1)

    update_json_field(sys.argv[1], sys.argv[2], sys.argv[3])
