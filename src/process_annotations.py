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
from utils.misc_helpers import read_jsonl_file, save_as_jsonl, read_partial_jsonl_file

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

def load_partial_results(partial_output_path):
    """
    Load the partial output file and return processed entries as a dictionary.
    
    Args:
        partial_output_path (str): Path to the partial output file.

    Returns:
        dict: A dictionary with processed data.
    """
    if os.path.exists(partial_output_path):
        logging.info(f"Resuming from existing partial output file: {partial_output_path}")
        return read_partial_jsonl_file(partial_output_path)
    return []

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
    os.makedirs(output_dir, exist_ok=True)

    # Read input data
    input_file_path = os.path.join(input_dir, input_file_name)
    logging.info(f"Reading input file: {input_file_path}")
    data = read_jsonl_file(input_file_path)

    # Load partial results
    partial_output_path = os.path.join(output_dir, partial_output_file_name)
    processed_data = load_partial_results(partial_output_path)
    
    logging.info(f"Loaded {len(processed_data)} processed entries from partial output file.")
    
    # Create a set of processed IDs to track progress
    processed_ids = {entry['recordId'] for entry in processed_data if 'recordId' in entry}

    # Filter unprocessed data
    data = [entry for entry in data if entry.get('recordId') not in processed_ids]
    
    logging.info(f"Processing {len(data)} new samples...")


    # Limit the number of samples if required
    if max_samples:
        data = data[:max_samples]

    if not data:
        logging.info("No new samples to process. Exiting...")
        return

    logging.info(f"Invoking endpoints for {len(data)} new samples...")

    # Process remaining data
    new_results = parallel_invoke_bedrock_endpoints(
        data,
        save_partial=True,
        partial_save_path=partial_output_path,
        save_interval=save_interval
    )

    # Append new results to the final output
    output_file_path = os.path.join(output_dir, output_file_name)
    logging.info(f"Saving results to: {output_file_path}")

    # Combine previous partial results with new results
    all_results = processed_data + new_results
    save_as_jsonl(all_results, output_file_path)

def main():
    parser = argparse.ArgumentParser(description="Process annotations using Bedrock endpoints.")
    parser.add_argument('--directory', type=str, required=True, help="Base directory for input and output files.")
    parser.add_argument('--split', type=str, required=True, choices=['train', 'test', 'validation'], help="Dataset split.")
    parser.add_argument('--model_name', type=str, required=True, help="Name of the model to use.")
    parser.add_argument('--file_nameId', type=str, required=True, help="Name of the qualifier.")
    parser.add_argument('--max_samples', type=int, default=None, help="Maximum number of samples to process.")
    parser.add_argument('--save_interval', type=int, default=100, help="Save at every N iteration.")

    args = parser.parse_args()

    input_dir = os.path.join(args.directory, f"inputs/annotator_requests/{args.split}")
    output_dir = os.path.join(args.directory, f"outputs/annotations/{args.split}")
    input_file_name = f"annotator_requests_{args.file_nameId}_{args.model_name}_{args.split}.jsonl"
    output_file_name = f"annotator_responses_{args.file_nameId}_{args.model_name}_{args.split}.jsonl"
    partial_output_file_name = f"annotator_responses_{args.file_nameId}_{args.model_name}_{args.split}_partial.jsonl"

    log_dir = os.path.join(args.directory, "logs")
    log_file_path = os.path.join(log_dir, f"log_{output_file_name}.log")
    setup_logging(log_file_path)

    logging.info("Starting annotation processing...")
    logging.info(f"Parameters: {args}")

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
