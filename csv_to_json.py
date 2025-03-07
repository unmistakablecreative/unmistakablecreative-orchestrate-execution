import csv
import json
import sys

def csv_to_json(csv_file, json_file):
    """Convert a CSV file to JSON format."""
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]  # Convert rows into a list of dictionaries
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)  # Save as formatted JSON

    print(f"✅ Successfully converted {csv_file} to {json_file}")

# Run from CLI: python csv_to_json.py input.csv output.json
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python csv_to_json.py <input_csv> <output_json>")
        sys.exit(1)

    csv_to_json(sys.argv[1], sys.argv[2])
