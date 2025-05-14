from openai import AzureOpenAI
import os
from dotenv import dotenv_values
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import time
from tqdm import tqdm
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

# Load environment variables
def load_environment_variables():
    dotenv_path = find_dotenv()
    if dotenv_path:
        secrets = dotenv_values(dotenv_path)
    else:
        raise FileNotFoundError(".env file not found in any parent directory")
    return secrets

# Initialize clients
def initialize_clients(secrets):
    personal_api_key = secrets['AZURE_OPENAI_KEY']
    azure_endpoint = secrets['AZURE_OPENAI_ENDPOINT']

    client = AzureOpenAI(
    azure_endpoint = azure_endpoint, 
    api_key=personal_api_key,  
    api_version="2024-02-15-preview"
    )
    return client

# Initialize logging
def initialize_logging(log_file='openai_logger.log'):
    logging.basicConfig(filename=log_file, level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)


# Function to log specific messages
def log_message(logger, message):
    logger.log(logging.INFO, message)

# function to run all above preprocessing operations/functions
def run_all_preprocessing():
    logger = initialize_logging()
    log_message(logger, "Starting all operations")
    secrets = load_environment_variables()
    return logger, initialize_clients(secrets)

# calling run all preprocessing function
logger, client = run_all_preprocessing()

def query_openai_model(prompt, model_name = "gpt4-turbo-0125"):
    response = client.chat.completions.create(
        model=model_name, # model = "deployment_name".
        temperature = 0.2,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{prompt}"}
        ],
        response_format={"type": "json_object"}
    )
    usage = response.usage

    return response.choices[0].message.content, usage

def query_openai_model_with_retries(prompt, model_name="gpt4-turbo-0125", max_retries=5):
    retry_count = 0
    wait_time = 1  # Start with 1 second wait time
    while retry_count < max_retries:
        try:
            response = client.chat.completions.create(
                model=model_name,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"{prompt}"}
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content, response.usage
        except Exception as e:
            logging.error(f"Error querying prompt '{prompt}': {e}")
            if "rate limit" in str(e).lower():
                retry_count += 1
                logging.info(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2  
            else:
                break  
    return None, None

def query_openai_model_batch(prompts, model_name="gpt4-turbo-0125", max_workers=5):
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(query_openai_model_with_retries, prompt, model_name): i for i, prompt in enumerate(prompts)}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing prompts"):
            idx = futures[future]
            try:
                result = future.result()
                results[idx] = result
            except Exception as e:
                logging.error(f"Error processing a future for prompt index {idx}: {e}")
                results[idx] = (None, None)
    return results

def query_openai_model_batch_save(prompts, model_name="gpt4-turbo-0125", max_workers=5, save_interval=500, save_path="outputs/results_temp"):
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(query_openai_model_with_retries, prompt, model_name): i for i, prompt in enumerate(prompts)}
        for i, future in enumerate(tqdm(as_completed(futures), total=len(futures), desc="Processing prompts")):
            idx = futures[future]
            try:
                result = future.result()
                results[idx] = result
            except Exception as e:
                logging.error(f"Error processing a future for prompt index {idx}: {e}")
                log_message(logger, f"Error processing a future for prompt index {idx}: {e}")
                results[idx] = (None, None)
                
            # Save the results every 'save_interval' iterations
            if (i + 1) % save_interval == 0:
                print('Saving intermediate results')
                log_message('Saving intermediate results')
                np.save(f'{save_path}', results)
                
    # Save final results
    np.save(f'{save_path}'+'_final', results)
    
    return results

# resp = query_openai_model("Are you up? reply in json")
# print(resp)