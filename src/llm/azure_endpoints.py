"""
This module handles Azure OpenAI and Phi-3/4 endpoint configurations and interactions.
"""
from openai import AzureOpenAI
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import dotenv_values
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
import numpy as np

def find_dotenv(start_path='.'):
    current_dir = os.path.abspath(start_path)
    while True:
        env_path = os.path.join(current_dir, '.env')
        if os.path.isfile(env_path):
            return env_path
        new_dir = os.path.dirname(current_dir)
        if new_dir == current_dir:  # Reached root
            return None
        current_dir = new_dir

# TODO: This preprocessing logic should not be in global scope. 
# We should have a function to load the environment variables and initialize the clients based on a config file.
# Initialize logging
logging.basicConfig(filename='azure_endpoints.log', level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_message(message):
    logger.log(logging.INFO, message)

# Load environment variables
dotenv_path = find_dotenv()
if dotenv_path:
    secrets = dotenv_values(dotenv_path)
else:
    raise FileNotFoundError(".env file not found in any parent directory")

# Initialize OpenAI client
openai_client = AzureOpenAI(
    azure_endpoint=secrets['AZURE_OPENAI_ENDPOINT'],
    api_key=secrets['AZURE_OPENAI_KEY'],
    api_version="2024-02-15-preview"
)

# Initialize Phi-3 client
phi3_client = ChatCompletionsClient(
    endpoint=secrets['AZURE_PHI3_ENDPOINT'],
    credential=AzureKeyCredential(secrets['AZURE_PHI3_KEY'])
)

# Initialize Phi-4 client
phi4_client = ChatCompletionsClient(
    endpoint=secrets['AZURE_PHI4_ENDPOINT'],
    credential=AzureKeyCredential(secrets['AZURE_PHI4_KEY'])
)

def query_with_retries(func, *args, max_retries=5, **kwargs):
    """
    Generic retry function for any query with exponential backoff
    """
    retry_count = 0
    wait_time = 1  # Start with 1 second wait time
    last_error = None

    while retry_count < max_retries:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            error_msg = str(e).lower()
            logging.error(f"Error in {func.__name__}: {e}")
            
            # Check for various error conditions that warrant a retry
            if any(err in error_msg for err in ['rate limit', 'timeout', 'connection', 'server']):
                retry_count += 1
                if retry_count < max_retries:
                    logging.info(f"Attempt {retry_count}/{max_retries}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    wait_time *= 2
            else:
                # If it's not a retryable error, break immediately
                break
    
    # If we've exhausted retries or hit a non-retryable error
    logging.error(f"Failed after {retry_count} retries. Last error: {last_error}")
    return None, None

def _query_openai(prompt, model_name="gpt4-turbo-0125", temperature=0.2):
    """
    Internal OpenAI query function
    """
    response = openai_client.chat.completions.create(
        model=model_name,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{prompt}"}
        ],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content, response.usage

def _query_phi3(prompt, max_tokens=1000, temperature=0.7):
    """
    Internal Phi-3 query function
    """
    response = phi3_client.complete(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.choices[0].message.content, None

def _query_phi4(prompt, max_tokens=1000, temperature=0.7):
    """
    Internal Phi-4 query function
    """
    response = phi4_client.complete(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.choices[0].message.content, None

def query_openai_model(prompt, model_name="gpt4-turbo-0125", temperature=0.2, max_retries=5):
    """
    Query Azure OpenAI model with given prompt and retry logic
    """
    return query_with_retries(_query_openai, prompt, model_name=model_name, 
                            temperature=temperature, max_retries=max_retries)

def query_phi3_model(prompt, max_tokens=1000, temperature=0.2, max_retries=5):
    """
    Query Phi-3 model with given prompt and retry logic
    """
    return query_with_retries(_query_phi3, prompt, max_tokens=max_tokens, 
                            temperature=temperature, max_retries=max_retries)

def query_phi4_model(prompt, max_tokens=1000, temperature=0.2, max_retries=5):
    """
    Query Phi-4 model with given prompt and retry logic
    """
    return query_with_retries(_query_phi4, prompt, max_tokens=max_tokens, 
                            temperature=temperature, max_retries=max_retries)

#test
resp = query_openai_model("Are you up? reply in json", model_name='gpt-4o-mini')
print(resp)  

#test
# resp = query_phi4_model("Are you up? reply in json")
# print(resp)

