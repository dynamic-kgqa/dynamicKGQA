import re
import json

import urllib.parse

def parse_yago_uri(uri):
    """
    Extracts answer and answer_readable from a YAGO URI, with unicode and underscore decoding.
    
    Args:
        uri (str): A URI from YAGO like "http://yago-knowledge.org/resource/Shane__u0028_film_u0029_"
    
    Returns:
        tuple: (answer, answer_readable)
    """
    # Step 1: Extract the final entity part from the URI
    answer = uri.split("/")[-1]
    
    # Step 2: Decode any Unicode escape sequences manually
    # Handle things like "__u0028_" -> " ("
    decoded = re.sub(r'_u([0-9a-fA-F]{4})_', lambda m: chr(int(m.group(1), 16)), answer)

    # Step 3: Replace remaining underscores with spaces (excluding ones in valid names)
    decoded = decoded.replace('_', ' ')
    
    return answer, decoded


def convert_to_json_object(original_string, model):
       
    if model == 'phi3':
        model_type = 'serverless'
    elif model == 'mistral':
        model_type = 'dedicated'
    elif model == 'llama3-8b':
        model_type = 'dedicated'
    else:
        raise Exception("Model details not found")
    
    if model_type == 'serverless':
        try:
            cleaned_string = original_string.replace('```json', '').replace('\n', '').replace('```', '') 
            # cleaned_string = original_string.replace("```json", "")
            cleaned_string = cleaned_string.strip("```json\n")
            # Use regex to strip the unwanted parts
            cleaned_string = re.sub(r"(^'```json\n|\n```'$)", '', cleaned_string).strip()

            # Further clean the string by removing additional newlines or surrounding quotes
            cleaned_string = cleaned_string.strip()

            # Convert string to JSON object
            json_object = json.loads(cleaned_string)
            return json_object
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
    elif model_type == 'dedicated':
        try:
            json_object = json.loads(original_string)
            result = json.loads(json_object['output'])
            return result
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
        
    else:
        print("Model details not found")
        return None