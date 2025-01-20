import boto3
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from botocore.exceptions import ClientError

# logger = logging.getLogger(__name__)
# logging.basicConfig(filename='/home/ec2-user/code_repos/dynamicKGQA/logs/bedrock_functions.log',
#                     level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1'
    )

def build_anthropic_request_body(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float = 0.0
) -> dict:
    """
    Builds the JSON payload for Anthropic Claude.

    :param system_prompt: Instructions or context for the system.
    :param user_prompt: The text of the user's request.
    :param max_tokens: The maximum number of tokens to generate.
    :param temperature: Sampling temperature (creativity control).
    :return: A dict representing the request body for Claude.
    """
    # For Anthropic on Bedrock, the required fields typically include:
    # - anthropic_version
    # - system (system instructions)
    # - messages (the conversation so far)
    # - max_tokens (or max_tokens_to_sample in older versions)
    # - Optionally: temperature, top_p, etc.

    # Note: If your particular Claude model expects a single combined prompt,
    # you can instead pass a single string in "prompt". This example uses
    # "system" and "messages" to reflect the multi-message format.
    

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    return request_body

def build_mistral_request_body(prompt: str, max_tokens: int = 2048, temperature: float = 0) -> dict:
    """
    Builds a minimal JSON payload for Mistral.

    :param prompt: The input text for the model.
    :param max_tokens: The maximum number of tokens to generate (default: 50).
    :param temperature: Sampling temperature for response variation (default: 0.7).
    :return: A dict representing the minimal request body.
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

def build_llama_request_body(
    prompt: str,
    max_tokens: int = 2048,
    temperature: float = 0
) -> dict:
    """
    Builds a minimal JSON payload for Llama for single-prompt inference.

    :param prompt: The input text for the model.
    :param max_gen_len: The maximum number of tokens to generate in the response (default: 512).
    :param temperature: Sampling temperature for response variation (default: 0.5).
    :param top_p: Nucleus sampling parameter for response diversity (default: 0.9).
    :return: A dict representing the minimal request body.
    """
    request_body = {
        "modelId": "us.meta.llama3-3-70b-instruct-v1:0",
        "contentType": "application/json",
        "accept": "application/json",
        "body": json.dumps({
            "prompt": prompt,
            "max_gen_len": max_tokens,
            "temperature": temperature
        })
    }
    return request_body


def build_command_r_request_body(
    prompt: str,
    max_tokens: int = 2048,
    temperature: float = 0
) -> dict:
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

def build_nova_request_body(
    prompt: str,
    max_tokens: int = 2048,
    temperature: float = 0
) -> dict:
    """
    Builds a minimal JSON payload for Amazon Nova for single-prompt inference.

    :param prompt: The input text for the model.
    :param max_new_tokens: The maximum number of tokens to generate in the response (default: 1000).
    :param temperature: Sampling temperature for response variation (default: 0.7).
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


def invoke_bedrock_endpoint(
    request_body: dict,
    model_id: str,
    region_name: str = "us-east-1",
    content_type = 'application/json',
    max_retries: int = 3,
    backoff_factor: float = 2.0
) -> dict:
    """
    Invokes the Bedrock endpoint with a given request body and model ID,
    with exponential backoff retries for transient errors.

    :param request_body: JSON payload specific to the chosen model.
    :param model_id: The Bedrock model ID, e.g. "anthropic.claude-v1".
    :param region_name: The AWS region to call. Default is "us-east-1".
    :param max_retries: Number of retry attempts for transient errors.
    :param backoff_factor: Factor for exponential backoff, e.g. 2.0 means
                           1s, 2s, 4s between retries, etc.
    :return: The deserialized JSON response from Bedrock.
    """
    

    for attempt in range(max_retries):
        try:

            response = bedrock_runtime.invoke_model(
                body=request_body,
                modelId=model_id,
                contentType=content_type
            )

            # The response body is a StreamingBody, so we need to read and decode it.
            response_body = json.loads(response.get('body').read())
            return response_body

        except ClientError as err:
            logger.error(
                "Error invoking Bedrock on attempt %s: %s",
                attempt + 1,
                err.response["Error"]["Message"]
            )

            # If this was the last attempt, re-raise the error.
            if attempt == max_retries - 1:
                raise

            # Otherwise, back off exponentially before retrying.
            sleep_time = backoff_factor ** attempt
            logger.info(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)



def parallel_invoke_bedrock_endpoints(
    requests_data: list,  
    # requests_data is a list of tuples: [(request_body1, model_id1), (request_body2, model_id2), ...]
    region_name="us-east-1",
    contentType="application/json",
    max_retries=3,
    backoff_factor=2.0,
    concurrency=5,
    save_partial=True,
    partial_save_path="partial_results.json",
    save_interval: int = 100
):
    """
    Invokes Bedrock endpoints in parallel using a thread pool, collects results,
    and optionally saves partial results as they complete. Now with tqdm progress.
    """
    results = [None] * len(requests_data)

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        future_to_index = {}
        
        
        
        # Submit all tasks
        for i, item in enumerate(requests_data):
            record_id = item["recordId"]
            model_input = item["modelInput"]

            # Extract relevant fields from modelInput
            model_id = model_input["modelId"]
            body = model_input["body"]
            content_type = model_input.get("contentType", "application/json")

            fut = executor.submit(
                invoke_bedrock_endpoint,
                model_id=model_id,
                request_body=body,
                content_type=content_type,
                region_name=region_name,
                max_retries=max_retries,
                backoff_factor=backoff_factor
            )
            future_to_index[fut] = i
            
        completed_count = 0
        total_tasks = len(future_to_index)

        # Track completion with tqdm
        with tqdm(total=len(future_to_index), desc="Requests Completed") as pbar:
            for future in as_completed(future_to_index):
                i = future_to_index[future]
                record_id = requests_data[i]["recordId"]

                try:
                    response_json = future.result()
                    results[i] = {
                        "recordId": record_id,
                        "response": response_json,
                        "error": None
                    }
                except Exception as exc:
                    logger.error(f"Request {record_id} failed: {exc}")
                    results[i] = {
                        "recordId": record_id,
                        "response": None,
                        "error": str(exc)
                    }

                # Update tqdm
                pbar.update(1)
                completed_count += 1

                # Optionally save partial
                # if save_partial:
                if save_partial and (
                    (completed_count % save_interval == 0) or
                    (completed_count == total_tasks)  # final iteration
                ):
                    try:
                        with open(partial_save_path, "w") as f:
                            json.dump(results, f, indent=2)
                        logger.info(f"Partial results saved to {partial_save_path}")
                    except Exception as e:
                        logger.error(f"Failed saving partial results: {e}")

    return results
