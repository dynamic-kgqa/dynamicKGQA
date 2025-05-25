from openai import AzureOpenAI
import os
from dotenv import dotenv_values
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import time
from tqdm import tqdm
import numpy as np
import json
from enum import Enum

from base_endpoint import BaseEndpoint

class OpenAIModelType(Enum):
    OPENAI = "openai"

# Define the OpenAIModel Enum to represent different OpenAI models
## Can be extended with specific models as needed
class OpenAIModel(Enum):
    pass

class OpenAIEndpoint(BaseEndpoint):
    """
    This class handles interactions with OpenAI endpoints.
    It initializes the client and provides methods to query the models.
    """
    def __init__(self, log_file: str = 'openai_endpoints.log'):
        self.secrets = self.load_env()
        self._load_logging(log_file=log_file)
        self.initialize_clients(self.secrets)

    # TODO: OpenAI endpoint should be utilizing the OpenAI endpoint instead of Azure OpenAI.
    def initialize_clients(self, secrets: dict):
        # Initialize OpenAI client
        self.openai_client = AzureOpenAI(
            azure_endpoint=secrets['AZURE_OPENAI_ENDPOINT'],
            api_key=secrets['AZURE_OPENAI_KEY'],
            api_version="2024-02-15-preview"
        )
    
    def query(self, prompt: str, model_type: OpenAIModelType, model_name: str, **kwargs) -> tuple:
        if model_type == OpenAIModelType.OPENAI:
            return self._query_openai(prompt, model_name=model_name, **kwargs)
        else:
            raise ValueError(f"Unsupported model type: {model_type}. Supported types: {OpenAIModelType.openai}")

    def _query_openai(self, prompt: str, model_name: str="gpt4-turbo-0125", temperature: float=0.2) -> tuple:
        """
        Internal OpenAI query function
        """
        try:
            response = self.openai_client.chat.completions.create(
                model=model_name,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"{prompt}"}
                ],
                response_format={"type": "json_object"}
            )
        except Exception as e:
            print(f"Error querying OpenAI model: {e}")
        return response.choices[0].message.content, response.usage

    def query_with_retries(self, prompt: str, model_type: OpenAIModelType, model_name: str, max_retries: int=5, **kwargs):
        return super().query_with_retries(prompt, model_type, model_name, max_retries=max_retries, **kwargs)

    def query_batch(self, prompts: str, model_type: OpenAIModelType, model_name: str, max_workers: int=5, **kwargs) -> dict:
        return super().query_batch(prompts, model_type, model_name, max_workers=max_workers, **kwargs)

    def query_batch_save(self, prompts: list[str], model_type, model_name, max_workers: int=5, save_interval: int=500, save_path: str="openai_results", **kwargs) -> None:
        super().query_batch_save(prompts, model_type, model_name, max_workers=max_workers, save_interval=save_interval, save_path=save_path, **kwargs)

if __name__ == "__main__":
    # Example usage
    openai_endpoint = OpenAIEndpoint()

    # Example query
    resp = openai_endpoint.query(prompt="Are you up? reply in json", model_type=OpenAIModelType.OPENAI, model_name='gpt4-turbo-0125')
    print(resp)

    # Example query with retries
    resp_with_retries = openai_endpoint.query_with_retries(prompt="Are you up? reply in json", model_type=OpenAIModelType.OPENAI, model_name='gpt4-turbo-0125', max_retries=3)
    print(resp_with_retries)

    # Example batch query
    prompts = ["What is the capital of France? reply in json", 
               "What is the largest mammal? reply in json", 
               "Who wrote 'To Kill a Mockingbird'? reply in json",
               "What is the boiling point of water? reply in json", 
               "What is the speed of light? reply in json", 
               "What is the currency of Japan? reply in json"]
    batch_results = openai_endpoint.query_batch(prompts, model_type=OpenAIModelType.OPENAI, model_name='gpt4-turbo-0125', max_workers=3)
    for idx, result in batch_results.items():
        print(f"Prompt {idx}: {result}")

    # Example batch query with saving results
    batch_results_save = openai_endpoint.query_batch_save(prompts, model_type=OpenAIModelType.OPENAI, model_name='gpt4-turbo-0125', max_workers=3, save_interval=3, save_path="openai_results")
