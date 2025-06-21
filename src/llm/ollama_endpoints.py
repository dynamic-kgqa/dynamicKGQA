import requests
import json
import re

# OLLAMA_BASE_URL = "http://localhost:11434"

def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    else:
        raise ValueError("No JSON object found in response.")

def query_ollama_model(prompt, model_name="llama3", port=11434):
    base_url = f"http://localhost:{port}"
    response = requests.post(
        f"{base_url}/api/chat",
        json={
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1000
        },
        stream=True   
    )
    contents = []
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode('utf-8'))
            if 'message' in data and 'content' in data['message']:
                contents.append(data['message']['content'])
            if data.get('done', False):
                break
    full_response = ''.join(contents)
    try:
        json_str = extract_json(full_response)
        parsed = json.loads(json_str)
        return parsed, full_response
    except Exception as e:
        # Return the raw string for debugging if parsing fails
        raise ValueError(f"Failed to parse JSON from model output: {e}\nRaw output: {full_response}")

# def main():
#     prompt = "Are you up? reply in json"
#     response, usage = query_ollama_model(prompt=prompt)
#     print("Response:", response)

# if __name__ == "__main__":
#     main()


