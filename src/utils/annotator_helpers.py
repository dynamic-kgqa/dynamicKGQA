from utils.azure_endpoints import query_openai_model, query_phi3_model, query_phi4_model
from utils.parsing_helpers import convert_to_json_object
import json

def ping_all_models(prompt):
    res_openai = query_openai_model(prompt)
    res_phi3 = query_phi3_model(prompt)
    res_phi4 = query_phi4_model(prompt)
    return res_openai, res_phi3, res_phi4


def get_model_annotations(prompt):
    try:
        annotator_gpt4_mini, usage = query_openai_model(prompt, model_name='gpt-4o-mini')
        try:
            # OpenAI responses should already be JSON formatted
            annotator_1 = json.loads(annotator_gpt4_mini)
        except json.JSONDecodeError:
            print("Failed to parse GPT-4-mini response as JSON")
            annotator_1 = None
    except Exception as e:
        print(f"Error getting GPT-4 annotation: {str(e)}")
        annotator_1 = None
        
    try:
        annotator_phi3, _ = query_phi3_model(prompt)
        annotator_2 = convert_to_json_object(annotator_phi3, 'phi3')
        if annotator_2 is None:
            print("Failed to convert Phi-3 response to JSON")
    except Exception as e:
        print(f"Error getting Phi-3 annotation: {str(e)}")
        annotator_2 = None

    try:
        annotator_gpt4, _ = query_openai_model(prompt)
        try:
            # OpenAI responses should already be JSON formatted
            annotator_3 = json.loads(annotator_gpt4)
        except json.JSONDecodeError:
            print("Failed to parse GPT-4 response as JSON")
            annotator_3 = None
    except Exception as e:
        print(f"Error getting GPT-4 annotation: {str(e)}")
        annotator_3 = None
        
    return annotator_1, annotator_2, annotator_3
