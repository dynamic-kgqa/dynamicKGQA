from llm.ollama_endpoints import query_ollama_model
from utils.parsing_helpers import convert_to_json_object
import json

def ping_ollama_model(prompt):
    return query_ollama_model(prompt)

def get_ollama_annotations(prompt):
    try:
        annotator, _ = query_ollama_model(prompt)
        annotator_ollama = convert_to_json_object(annotator, 'ollama')
        if annotator_ollama is None:
            print("Failed to convert Ollama response to JSON")
    except Exception as e:
        print(f"Error getting Ollama annotation: {str(e)}")
        return None
    return annotator_ollama