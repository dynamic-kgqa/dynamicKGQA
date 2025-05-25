import boto3
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from botocore.exceptions import ClientError
import json
from enum import Enum

from base_endpoint import BaseEndpoint

class BedrockModelType(Enum):
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"
    LLAMA = "llama"
    COMMAND_R = "command_r"
    NOVA = "nova"

# Define the BedrockModel Enum to represent different Bedrock models
## Can be extended with specific models as needed
class BedrockModel(Enum):
    pass

class BedrockEndpoint(BaseEndpoint):
    """
    This class handles interactions with Amazon Bedrock endpoints.
    It initializes the client and provides methods to query the models.
    """
    def __init__(self, log_file: str = 'bedrock_endpoints.log'):
        self.secrets = self.load_env()
        self._load_logging(log_file=log_file)
        self.initialize_clients(self.secrets)

    def initialize_clients(self, secrets: dict):
        # Initialize Bedrock client
        self.bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=secrets['AWS_REGION'],
        )

    def query(self, prompt: str, model_type: BedrockModelType, model_name: str=None, **kwargs) -> tuple:
        """
        TODO: For each sub-method, add model_name as the model_id parameter.
        For now, we will keep it hard-coded for each model type.
        """
        max_tokens = kwargs.get('max_tokens', 1024)
        temperature = kwargs.get('temperature', 0.0)

        request_body = None
        if model_type == BedrockModelType.ANTHROPIC:
            request_body = self._build_anthropic_request_body(prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)
        elif model_type == BedrockModelType.MISTRAL:
            request_body = self._build_mistral_request_body(prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)
        elif model_type == BedrockModelType.LLAMA:
            request_body = self._build_llama_request_body(prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)
        elif model_type == BedrockModelType.COMMAND_R:
            request_body = self._build_command_r_request_body(prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)
        elif model_type == BedrockModelType.NOVA:
            request_body = self._build_nova_request_body(prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)
        else:
            raise ValueError(f"Unsupported model type: {model_type}. Supported types: {BedrockModelType.ANTHROPIC}, {BedrockModelType.MISTRAL}, {BedrockModelType.LLAMA}, {BedrockModelType.COMMAND_R}, {BedrockModelType.NOVA}")
        if request_body is None:
            raise ValueError("Request body could not be built. Please check the model type and parameters.")
        
        response = self.bedrock_client.invoke_model(
            body=request_body["body"],
            modelId=request_body["modelId"],
            contentType=request_body["contentType"],
            accept=request_body["accept"]
        )
        response_body = json.loads(response.get('body').read())
        # NOTE: Return None for usage for now.
        return response_body, None

    def _build_anthropic_request_body(self, prompt: str, system_prompt: str = None, 
                                      max_tokens: int = 1024, temperature: float = 0.0,
                                      **kwargs) -> dict:
        """
        Builds the JSON payload for Anthropic Claude.

        :param system_prompt: Instructions or context for the system.
        :param user_prompt: The text of the user's request.
        :param max_tokens: The maximum number of tokens to generate.
        :param temperature: Sampling temperature (creativity control).
        :return: A dict representing the request body for Claude.
        """
        system_prompt = system_prompt or "You are a helpful assistant."
        request_body = {
            "modelId": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            "contentType": "application/json",
            "accept": "application/json",
            "body": json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                # "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            })
        }
        return request_body

    def _build_mistral_request_body(self, prompt: str, max_tokens: int = 2048, temperature: float = 0,
                                     **kwargs) -> dict:
        """
        Builds the JSON payload for Mistral models.

        :param prompt: The text of the user's request.
        :param max_tokens: The maximum number of tokens to generate.
        :param temperature: Sampling temperature (creativity control).
        :return: A dict representing the request body for Mistral.
        """
        request_body = {
            "modelId": "mistral.mistral-small-2402-v1:0",
            "contentType": "application/json",
            "accept": "application/json",
            "body": json.dumps({
                "prompt": f"<s>[INST] {prompt} [/INST]",
                "max_tokens": max_tokens, 
                "temperature": temperature
            })
        }
        return request_body
    
    def _build_llama_request_body(self, prompt: str, max_tokens: int = 2048, temperature: float = 0,
                                   **kwargs) -> dict:
        """
        Builds a minimal JSON payload for Llama for single-prompt inference.

        :param prompt: The input text for the model.
        :param max_gen_len: The maximum number of tokens to generate in the response (default: 512).
        :param temperature: Sampling temperature for response variation (default: 0.5).
        :param top_p: Nucleus sampling parameter for response diversity (default: 0.9).
        :return: A dict representing the minimal request body.
        """
        request_body = {
            "modelId": "us.meta.llama3-2-3b-instruct-v1:0",
            "contentType": "application/json",
            "accept": "application/json",
            "body": json.dumps({
                "prompt": prompt,
                "max_gen_len": max_tokens,
                "temperature": temperature
            })
        }
        return request_body
    
    def _build_command_r_request_body(self, prompt: str, max_tokens: int = 2048, temperature: float = 0,
                                      **kwargs) -> dict:
        """
        Builds a minimal JSON payload for Command-R for single-prompt inference.

        :param prompt: The input text for the model.
        :param max_tokens: The maximum number of tokens to generate (default: 50).
        :param temperature: Sampling temperature for response variation (default: 0.7).
        :return: A dict representing the minimal request body.
        """
        request_body = {
            "modelId": "cohere.command-r-v1:0",
            "contentType": "application/json",
            "accept": "*/*",
            "body": json.dumps({
                "message": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            })
        }
        return request_body
    
    def _build_nova_request_body(self, prompt: str, max_tokens: int = 2048, temperature: float = 0,
                                  **kwargs) -> dict:
        """
        Builds a minimal JSON payload for Amazon Nova for single-prompt inference.

        :param prompt: The input text for the model.
        :param max_new_tokens: The maximum number of tokens to generate in the response (default: 1000).
        :param temperature: Sampling temperature for response variation (default: 0).
        :return: A dict representing the request body, with the 'body' serialized as a JSON string.
        """
        # Build the request body
        request_body = {
            "modelId": "amazon.nova-lite-v1:0",
            "contentType": "application/json",
            "accept": "application/json",
            "body": json.dumps({  # Serialize the body as JSON string
                "inferenceConfig": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature
                },
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            })
        }
        return request_body