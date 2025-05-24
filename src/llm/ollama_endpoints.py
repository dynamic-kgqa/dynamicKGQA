import requests
import json

OLLAMA_BASE_URL = "http://localhost:11434"

def query_ollama_model(prompt, model_name="llama3"):
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
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
    return ''.join(contents), None

# def main():
#     prompt = "Are you up? reply in json"
#     response, usage = query_ollama_model(prompt=prompt)
#     print("Response:", response)

# if __name__ == "__main__":
#     main()


