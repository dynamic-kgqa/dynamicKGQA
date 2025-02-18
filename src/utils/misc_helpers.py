import json
import re
from tqdm import tqdm

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

def read_partial_jsonl_file(file_path):
    """
    Read a JSONL file or JSON array and return a list of JSON objects with a progress bar.

    Args:
        file_path (str): Path to the JSONL or JSON file.

    Returns:
        list: A list of JSON objects.
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            # Attempt to load the entire file as a JSON array
            data = json.load(file)
        except json.JSONDecodeError:
            # Fallback to reading as JSONL
            file.seek(0)
            total_lines = sum(1 for _ in file)
            file.seek(0)
            
            for line in tqdm(file, total=total_lines, desc=f"Reading {file_path}"):
                line = line.strip()
                if not line:
                    continue  # Skip empty lines
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue  # Skip invalid JSON lines silently
    data = [entry for entry in data if entry is not None]      
    return data

# read json file
def read_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

    
def parse_json_from_text(text):
    """
    Extracts and parses a JSON string embedded in a text block and returns it as a Python dictionary.
    If any error occurs, it returns None.

    Args:
        text (str): The input text containing the JSON block.

    Returns:
        dict or None: A dictionary representation of the JSON content, or None if an error occurs.
    """
    try:
        if not isinstance(text, str):
            # Input must be a string
            # print("Error: Input must be a string.")
            return None

        # Find the JSON part within the text
        start = text.find('{')
        end = text.find('}', start) + 1

        if start == -1 or end == 0:
            # No valid JSON found
            # print("Error: No valid JSON found in the input text.")
            return None

        # Extract the JSON string
        json_str = text[start:end]

        # Parse the JSON string into a dictionary
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        # print(f"Error: Failed to parse JSON - {e}")
        return None
    except Exception as e:
        # Handle other unforeseen errors
        # print(f"Unexpected error: {e}")
        return None
    
   
def parse_json_from_text_adict(text):
    """
    Extracts and parses a JSON string embedded in a text block and returns it as a Python dictionary.
    If any error occurs, it returns None.

    Args:
        text (str): The input text containing the JSON block.

    Returns:
        dict or None: A dictionary representation of the JSON content, or None if an error occurs.
    """
    try:
        if not isinstance(text, str):
            # Input must be a string
            # print("Error: Input must be a string.")
            return None

        # # Find the JSON part within the text
        # start = text.find('{')
        # end = text.find('}', start) + 1

        # if start == -1 or end == 0:
        #     # No valid JSON found
        #     # print("Error: No valid JSON found in the input text.")
        #     return None

        # Extract the JSON string
        text = text.replace("```json", "").replace("```", "")
        
        try:
            json_resp = json.loads(text)
            return json_resp
        except json.JSONDecodeError:
            # Fallback to safely_load_json if direct parsing fails
            # print("Direct JSON parsing failed, trying safe load.")
            return safely_load_json(text)

    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        # print(f"Error: Failed to parse JSON - {e}")
        return None
    except Exception as e:
        # Handle other unforeseen errors
        # print(f"Unexpected error: {e}")
        return None
    
def check_dict_structure_qdict(input_dict):
    """
    Checks if the input dictionary contains the same keys as the given structure.

    Args:
        input_dict (dict): The dictionary to be checked.

    Returns:
        bool: True if the structure matches, False otherwise.
    """
    # Define the template dictionary structure
    template_structure = {
        'question': str,
        'logical_structure_flag': bool,
        'logical_structure_reasoning': str,
        'redundancy_flag': bool,
        'redundancy_reasoning': str,
        'multiple_answers_flag': bool,
        'multiple_answers_reasoning': str
    }

    # Check if the input is a dictionary
    if not isinstance(input_dict, dict):
        # print("Error: Input is not a dictionary.")
        return False

    # Check if all keys in the template are in the input dictionary
    for key, value_type in template_structure.items():
        if key not in input_dict:
            # print(f"Error: Missing key '{key}' in the input dictionary.")
            return False
        if not isinstance(input_dict[key], value_type):
            # print(f"Error: Key '{key}' has incorrect type. Expected {value_type}, got {type(input_dict[key])}.")
            return False

    # Check for extra keys in the input dictionary
    extra_keys = set(input_dict.keys()) - set(template_structure.keys())
    if extra_keys:
        # print(f"Error: Extra keys found in the input dictionary: {extra_keys}")
        return False

    return True


def check_dict_structure_adict(input_dict):
    """
    Checks if the input dictionary contains the same keys as the given structure.

    Args:
        input_dict (dict): The dictionary to be checked.

    Returns:
        bool: True if the structure matches, False otherwise.
    """
    # Define the template dictionary structure
    template_structure = {
        # "question": str,
        # "answer": str,
        # "supporting_facts": list,
        "answer_support_flag": bool,
        "answer_support_reasoning": str,
        "answer_adequacy_flag": bool,
        "answer_adequacy_reasoning": str,
        }


    # Check if the input is a dictionary
    if not isinstance(input_dict, dict):
        print("Error: Input is not a dictionary.")
        return False

    # Check if all keys in the template are in the input dictionary
    for key, value_type in template_structure.items():
        if key not in input_dict:
            print(f"Error: Missing key '{key}' in the input dictionary.")
            return False
        if not isinstance(input_dict[key], value_type):
            print(f"Error: Key '{key}' has incorrect type. Expected {value_type}, got {type(input_dict[key])}.")
            return False

    # Check for extra keys in the input dictionary
    extra_keys = set(input_dict.keys()) - set(template_structure.keys())
    if extra_keys:
        print(f"Error: Extra keys found in the input dictionary: {extra_keys}")
        return False

    return True


def extract_json_block(text):
    """
    Extracts a JSON object from a fenced code block labeled ```json in the given text.
    
    Parameters:
        text (str): The text potentially containing a JSON code block.

    Returns:
        dict or None: The parsed JSON object as a Python dictionary,
                      or None if no valid JSON block is found.
    
    Raises:
        ValueError: If the JSON block is malformed or cannot be parsed.
    """
    # Regex pattern to capture the content between ```json and the closing ```
    pattern = r'```json\s*(.*?)\s*```'
    match = re.search(pattern, text, re.DOTALL)

    if not match:
        return None  # No JSON block found

    json_str = match.group(1).strip()#.replace("'", '"')

    try:
        data = json.loads(json_str)
        # json_data = ast.literal_eval(json_str)
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")


def process_responses_for_qcheck(res, model):

    failed_responses = []
    combined_results = []

    template_structure = {
            'question': "NA",
            'logical_structure_flag': None,
            'logical_structure_reasoning': "NA",
            'redundancy_flag': None,
            'redundancy_reasoning': "NA",
            'multiple_answers_flag': None,
            'multiple_answers_reasoning': "NA"
        }


    for i in tqdm(range(len(res))):
        if model == 'command_r':
            response = res[i]['response']['text']
            
        elif model == 'mistral':
            response = res[i]['response']['outputs'][0]['text']
            
        elif model == 'llama323b':
            response = res[i]['response']['generation']
            
        elif model == 'nova':
            response = res[i]['response']['output']['message']['content'][0]['text']
        
        parsed_dict = parse_json_from_text(response)
        
        if parsed_dict is None:
            failed_responses.append((i, res[i]))
            combined_results.append(template_structure)
            continue
        
        valid_structure = check_dict_structure_qdict(parsed_dict)
        if not valid_structure:
            failed_responses.append((i, res[i]))
            combined_results.append(template_structure)
            continue
        combined_results.append(parsed_dict)
    print(f"Failed responses: {len(failed_responses)}")
    
    return combined_results, failed_responses



def process_responses_for_qa_check(res, model):

    failed_responses = []
    combined_results = []

    template_structure = {
        # "question": "NA",
        # "answer": "NA",
        # "supporting_facts": [],
        "answer_support_flag": None,
        "answer_support_reasoning": "NA",
        "answer_adequacy_flag": None,
        "answer_adequacy_reasoning": "NA",
        }


    for i in tqdm(range(len(res))):
        if model == 'command_r':
            response = res[i]['response']['text']
            
        elif model == 'mistral':
            response = res[i]['response']['outputs'][0]['text']
            
        elif model == 'llama323b':
            response = res[i]['response']['generation']
            
        elif model == 'nova':
            response = res[i]['response']['output']['message']['content'][0]['text']
        
        parsed_dict = parse_json_from_text(response)
        
        if parsed_dict is None:
            failed_responses.append((i, res[i]))
            combined_results.append(template_structure)
            continue
        
        valid_structure = check_dict_structure_adict(parsed_dict)
        if not valid_structure:
            failed_responses.append((i, res[i]))
            combined_results.append(template_structure)
            continue
        combined_results.append(parsed_dict)
    print(f"Failed responses: {len(failed_responses)}")
    
    return combined_results, failed_responses

def process_responses_for_inference(res, model):

    failed_responses = []
    combined_results = []



    for i in tqdm(range(len(res))):
        try:
            if model == 'command_r':
                response = res[i]['response']['text']
                
            elif model == 'mistral':
                response = res[i]['response']['outputs'][0]['text']
                
            elif model == 'llama323b':
                response = res[i]['response']['generation']
                
            elif model == 'nova':
                response = res[i]['response']['output']['message']['content'][0]['text']
            
            elif model == 'anthropic':
                response = res[i]['modelOutput']['content'][0]['text']
                
            elif model == 'openai':
                response = res[i]['response']['body']['choices'][0]['message']['content']
                
            elif model == 'openai-gpt4o-mini':
                response = res[i]['response']['body']['choices'][0]['message']['content']
            
            
            if response is None:
                failed_responses.append((i, res[i]))
                # combined_results.append(None)
                combined_results.append("")
                continue
            combined_results.append(response)
        except Exception as e:
            
            failed_responses.append((i, res[i]))
            # combined_results.append(None)
            combined_results.append("")
            print(f"Failed for index: {i}, with error: {e}")
            continue
        
        
    print(f"Failed responses: {len(failed_responses)}")
    
    return combined_results, failed_responses