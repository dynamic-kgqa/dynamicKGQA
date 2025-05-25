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
from enum import Enum

# FIXME: Once the entire codebase is bundled into a package, we can support relative imports.
if __name__=='__main__':
    if __package__ is None:
        from os import path
        import sys
        sys.path.insert(0, path.dirname( path.abspath(__file__) ) )
        from base_endpoint import BaseEndpoint
    else:
        from .base_endpoint import BaseEndpoint
else:
    # We assume this is always called from src directory
    from llm.endpoints.base_endpoint import BaseEndpoint

class AzureModelType(Enum):
    OPENAI = "openai"
    PHI3 = "phi3"
    PHI4 = "phi4"

# TODO: Define the AzureModel Enum to represent different Azure models
## Can be extended with specific models as needed
class AzureModel(Enum):
    pass

class AzureEndpoint(BaseEndpoint):
    """
    This class handles interactions with Azure OpenAI and Phi-3/4 endpoints.
    It initializes the clients and provides methods to query the models.
    """
    def __init__(self, log_file: str = 'azure_endpoints.log'):
        self.secrets = self.load_env()
        self._load_logging(log_file=log_file)
        self.initialize_clients(self.secrets)

    def initialize_clients(self, secrets: dict):
        # Initialize OpenAI client
        self.openai_client = AzureOpenAI(
            azure_endpoint=secrets['AZURE_OPENAI_ENDPOINT'],
            api_key=secrets['AZURE_OPENAI_KEY'],
            api_version="2024-02-15-preview"
        )
        # Initialize Phi-3 client
        self.phi3_client = ChatCompletionsClient(
            endpoint=secrets['AZURE_PHI3_ENDPOINT'],
            credential=AzureKeyCredential(secrets['AZURE_PHI3_KEY'])
        )
        # Initialize Phi-4 client
        self.phi4_client = ChatCompletionsClient(
            endpoint=secrets['AZURE_PHI4_ENDPOINT'],
            credential=AzureKeyCredential(secrets['AZURE_PHI4_KEY'])
        )
    
    def query(self, prompt: str, model_type: AzureModelType, model_name: str=None, **kwargs) -> tuple:
        """
        Query the specified model with the given prompt.
        """
        if model_type == AzureModelType.OPENAI:
            return self._query_openai(prompt, model_name=model_name, **kwargs)
        elif model_type == AzureModelType.PHI3:
            return self._query_phi3(prompt, **kwargs)
        elif model_type == AzureModelType.PHI4:
            return self._query_phi4(prompt, **kwargs)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def _query_openai(self, prompt: str, model_name: str="gpt4-turbo-0125", temperature: float=0.2) -> tuple:
        """
        Internal OpenAI query function
        """
        response = self.openai_client.chat.completions.create(
            model=model_name,
            temperature=temperature,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{prompt}"}
            ],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content, response.usage
    
    def _query_phi3(self, prompt: str, max_tokens: int=1000, temperature: float=0.7) -> tuple:
        """
        Internal Phi-3 query function
        """
        response = self.phi3_client.complete(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content, None
    
    def _query_phi4(self, prompt: str, max_tokens: int=1000, temperature: float=0.7) -> tuple:
        """
        Internal Phi-4 query function
        """
        response = self.phi4_client.complete(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content, None

    def query_with_retries(self, prompt: str, model_type: AzureModelType, model_name: str, max_retries: int=5, **kwargs) -> tuple:
        return super().query_with_retries(prompt, model_type, model_name, max_retries, **kwargs)
    
    def query_batch(self, prompts: str, model_type: AzureModelType, model_name: str, max_workers: int=5, **kwargs) -> dict:
        return super().query_batch(prompts, model_type, model_name, max_workers=max_workers, **kwargs)

    def query_batch_save(self, prompts: list[str], model_type, model_name, max_workers: int=5, save_interval: int=500, save_path: str="openai_results", **kwargs) -> None:
        super().query_batch_save(prompts, model_type, model_name, max_workers=max_workers, save_interval=save_interval, save_path=save_path, **kwargs)
    
if __name__ == "__main__":
    # Initialize the AzureEndpoint
    azure_endpoint = AzureEndpoint()
    
    # Example usage of querying OpenAI model
    resp = azure_endpoint.query("Are you up? reply in json", model_type=AzureModelType.OPENAI, model_name='gpt4-turbo-0125')
    print(resp)

    # Example usage of querying with retries
    resp_with_retries = azure_endpoint.query_with_retries("Are you up? reply in json", model_type=AzureModelType.OPENAI, model_name='gpt4-turbo-0125')
    print(resp_with_retries)
