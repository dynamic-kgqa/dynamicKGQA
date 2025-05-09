"""
This module processes annotations using Bedrock endpoints.
"""
import os
import json
import argparse
import logging
from tqdm import tqdm
import pandas as pd


from llm.bedrock_functions import parallel_invoke_bedrock_endpoints
from utils.misc_helpers import read_jsonl_file, save_as_jsonl

# Set up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_logging(log_file_path):
    """
    Set up logging configuration to log both to console and a file.
    
    Args:
        log_file_path (str): Path to the log file.
    """
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_path, mode='w'),
            logging.StreamHandler()
        ]
    )

def process_annotations(input_dir, output_dir, input_file_name, output_file_name, partial_output_file_name, model_name, max_samples=None, save_interval=100):
    """
    Process annotations by invoking bedrock endpoints and saving results.
    
    Args:
        input_dir (str): Path to the input directory.
        output_dir (str): Path to the output directory.
        input_file_name (str): Name of the input file.
        output_file_name (str): Name of the output file.
        partial_output_file_name (str): Name of the partial output file.
        model_name (str): Model name to be used.
        max_samples (int, optional): Limit the number of samples processed.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Read input data
    input_file_path = os.path.join(input_dir, input_file_name)
    logging.info(f"Reading input file: {input_file_path}")
    data = read_jsonl_file(input_file_path)

    # Optionally limit the number of samples
    if max_samples:
        data = data[:max_samples]

    # Process data
    logging.info(f"Invoking endpoints for {len(data)} samples...")
    results = parallel_invoke_bedrock_endpoints(
        data,
        save_partial=True,
        partial_save_path=os.path.join(output_dir, partial_output_file_name),
        save_interval=save_interval
    )

    # Save results
    output_file_path = os.path.join(output_dir, output_file_name)
    logging.info(f"Saving results to: {output_file_path}")
    save_as_jsonl(results, output_file_path)

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process inference requests using Bedrock endpoints.")
    parser.add_argument('--directory', type=str, required=True, help="Base directory for input and output files.")
    parser.add_argument('--dataset', type=str, required=True, help="Dataset name.")
    parser.add_argument('--model_name', type=str, required=True, help="Name of the model to use.")
    parser.add_argument('--prompt_method', type=str, required=True, help="Name of the prompting method.")
    parser.add_argument('--max_samples', type=int, default=None, help="Maximum number of samples to process.")
    parser.add_argument('--save_interval', type=int, default=None, help="Save at every N iteration.")
    #inputs/inference_requests/SimpleQA/inference_requests_anthropic_SimpleQA_CoT.jsonl
    args = parser.parse_args()

    # Define paths and filenames
    input_dir = os.path.join(args.directory, f"inputs/inference_requests/{args.dataset}")
    output_dir = os.path.join(args.directory, f"outputs/inference_results/{args.dataset}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    input_file_name = f"inference_requests_{args.model_name}_{args.dataset}_{args.prompt_method}.jsonl"
    output_file_name = f"inference_responses_{args.model_name}_{args.dataset}_{args.prompt_method}.jsonl"
    partial_output_file_name = f"inference_responses_{args.model_name}_{args.dataset}_{args.prompt_method}_partial.jsonl"

    # Define log file
    log_dir = os.path.join(args.directory, "logs")
    log_file_path = os.path.join(log_dir, f"log_{output_file_name}.log")
    setup_logging(log_file_path)

    logging.info("Starting inferencing...")
    logging.info(f"Parameters: {args}")


    # Process annotations
    process_annotations(
        input_dir=input_dir,
        output_dir=output_dir,
        input_file_name=input_file_name,
        output_file_name=output_file_name,
        partial_output_file_name=partial_output_file_name,
        model_name=args.model_name,
        max_samples=args.max_samples,
        save_interval=args.save_interval
    )

if __name__ == "__main__":
    main()
