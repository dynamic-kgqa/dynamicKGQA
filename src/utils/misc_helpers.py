import json
import os

def save_as_jsonl(data, file_path):
    """
    Saves a list of dictionaries to a .jsonl file.

    Args:
        data (list): A list of dictionaries to be saved.
        file_path (str): Path to the output .jsonl file.

    Raises:
        ValueError: If the data is not a list of dictionaries.
    """
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError("Input data must be a list of dictionaries.")

    with open(file_path, 'w') as file:
        for entry in data:
            file.write(json.dumps(entry) + '\n')
            
def read_jsonl_file(file_path):
    """
    Reads a JSON Lines (JSONL) file where each line is a separate JSON object.
    Returns a list of Python dictionaries (or other data structures if the JSON
    objects are not strictly dictionaries).
    
    :param file_path: Path to the .jsonl file
    :return: A list of deserialized JSON objects
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:  # Skip any empty lines
                data.append(json.loads(line))
    return data