import json
import os

def count_chunks(json_file):
    """Counts the number of chunks in a JSON file."""
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if isinstance(data, list):
            print(f"✅ The file '{json_file}' contains {len(data)} chunks.")
        else:
            print("❌ The JSON structure is unexpected. Ensure it's a list of chunks.")
    except FileNotFoundError:
        print(f"❌ File '{json_file}' not found.")
    except json.JSONDecodeError:
        print(f"❌ Error decoding JSON in '{json_file}'. Ensure the file is valid JSON.")

# Usage example
if __name__ == "__main__":
    json_path = os.path.join(os.path.dirname(__file__),  "chunks.json")
    count_chunks(json_path)