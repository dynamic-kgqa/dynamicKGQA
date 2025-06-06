from llm.ollama_endpoints import query_ollama_model
import json
import re

def extract_json_from_response_block(block):
    """Extract and parse the first JSON object in a Markdown-style or raw string."""
    match = re.search(r'```(?:json)?\s*({[\s\S]*?})\s*```', block)
    if match:
        json_str = match.group(1)
    else:
        match = re.search(r'({[\s\S]*?})', block)
        if not match:
            raise ValueError("No JSON object found in response block:\n" + block)
        json_str = match.group(1)

    try:
        return json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Failed to parse extracted JSON:\n{json_str}\nError: {e}")


def get_ollama_annotations(prompt):
    annotations = []
    for i in range(3):
        raw, _ = query_ollama_model(prompt, model_name="llama3")
        # print(f"🧠 Annotator {i+1} raw response:\n{raw}\n")

        if isinstance(raw, dict):
            parsed = raw
        elif isinstance(raw, str):
            parsed = extract_json_from_response_block(raw)
        else:
            raise TypeError(f"Unexpected type from model: {type(raw)}")

        annotations.append(parsed)

    return tuple(annotations)


def main():
    prompt = "Give me a JSON object with your name and a greeting, e.g. {\"name\": \"Ollama\", \"greeting\": \"Hello!\"}"
    try:
        annotator_1, annotator_2, annotator_3 = get_ollama_annotations(prompt)
        print("Annotator 1:", annotator_1)
        print("Annotator 2:", annotator_2)
        print("Annotator 3:", annotator_3)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()