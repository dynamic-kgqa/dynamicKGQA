import os
from dotenv import dotenv_values
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import numpy as np

from abc import ABC, abstractmethod
from enum import Enum
from typing import Type, TypeVar

T = TypeVar('T', bound=Enum)

class BaseEndpoint(ABC):
    """
    Base class to interact with a specific LLM endpoint.
    This class should be extended for each specific LLM endpoint.
    """
    @abstractmethod
    def __init__(self, **kwargs):
        """
        Initialize the BaseEndpoint class.
        This method should be overridden by subclasses to set up the specific endpoint.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def _find_dotenv(self, start_path: str='.') -> str:
        """
        Find the .env file starting from the given path and going up the directory tree.
        """
        current_dir = os.path.abspath(start_path)
        while True:
            env_path = os.path.join(current_dir, '.env')
            if os.path.isfile(env_path):
                return env_path
            new_dir = os.path.dirname(current_dir)
            if new_dir == current_dir:
                return None
            current_dir = new_dir

    def load_env(self) -> dict:
        """
        Load environment variables from the .env file.
        Raises FileNotFoundError if the .env file is not found.
        """
        dotenv_path = self._find_dotenv()
        if dotenv_path:
            return dotenv_values(dotenv_path)
        else:
            raise FileNotFoundError(".env file not found in any parent directory")

    @abstractmethod
    def initialize_clients(self, secrets: dict) -> None:
        """
        Initialize the clients for the specific LLM endpoint.
        This method should be overridden by subclasses to set up the specific clients.

        TODO: Make this method more flexible to allow it to be called outside of the constructor
        as well as allow the re-initialization of only specific clients.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def _load_logging(self, log_file: str='base_endpoints.log') -> None:
        """
        Initialize logging for the endpoint interactions.
        Logs will be written to the specified log file.
        """
        # FIXME: logging.basicConfig is a convenience method intended for use by simple scripts
        # to do one-shot configuration of the logging package.
        # For more complex applications, it is recommended to use a more sophisticated logging setup.
        logging.basicConfig(filename=log_file, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def log_message(self, message: str) -> None:
        """
        Log a message to the logger.
        """
        self.logger.log(logging.INFO, message)

    def log_error(self, message: str) -> None:
        """
        Log an error message to the logger.
        """
        self.logger.log(logging.ERROR, message)

    @abstractmethod
    def query(self, prompt: str, model_type: Type[T], model_name: str, **kwargs) -> tuple:
        """
        Query the LLM endpoint with a given prompt and model name.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def query_with_retries(self, prompt: str, model_type: Type[T], model_name: str, max_retries: int, **kwargs):
        retry_count = 0
        wait_time = 1  # Start with 1 second wait time
        last_error = None

        while retry_count < max_retries:
            try:
                return self.query(prompt, model_type, model_name, **kwargs)
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                self.log_error(f"Error in querying {model_type.value} model: {e}")
                
                # Check for various error conditions that warrant a retry
                if any(err in error_msg for err in ['rate limit', 'timeout', 'connection', 'server']):
                    retry_count += 1
                    if retry_count < max_retries:
                        self.log_message(f"Attempt {retry_count}/{max_retries}. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        wait_time *= 2
                else:
                    # If it's not a retryable error, break immediately
                    break
        # If we've exhausted retries or hit a non-retryable error
        self.log_error(f"Failed after {retry_count} retries. Last error: {last_error}")
        return None, None

    def query_batch(self, prompts: list[str], model_type: Type[T], model_name: str, max_workers: int, **kwargs) -> dict:
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.query_with_retries, prompt, model_type, model_name, **kwargs): i
                for i, prompt in enumerate(prompts)
            }
            for i, future in enumerate(tqdm(as_completed(futures), total=len(futures), desc="Processing prompts")):
                try:
                    result = future.result()
                    idx = futures[future]
                    results[idx] = result
                except Exception as e:
                    self.log_error(f"Error processing a future for prompt index {idx}: {e}")
                    results[idx] = (None, None)
        return results
    
    def query_batch_save(self, prompts: list[str], model_type: Type[T], model_name: str, max_workers: int, save_interval: int, save_path: str, **kwargs) -> None:
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.query_with_retries, prompt, model_type, model_name, **kwargs): i
                for i, prompt in enumerate(prompts)
            }
            for i, future in enumerate(tqdm(as_completed(futures), total=len(futures), desc="Processing prompts")):
                try:
                    result = future.result()
                    idx = futures[future]
                    results[idx] = result
                except Exception as e:
                    self.log_error(f"Error processing a future for prompt index {idx}: {e}")
                    results[idx] = (None, None)
                # Save results to a file
                if (i + 1) % save_interval == 0:
                    self.log_message(f"Saving results after processing {i + 1} prompts.")
                    self._save_results(results, save_path, save_file_path=f"results_temp_{i + 1}.npy")
        # Save final results
        self._save_results(results, save_path, save_file_path='final_results.npy')

    def _save_results(self, results: dict, save_path: str, save_file_path: str = 'results.npy'):
        """
        Save results to a specified path.
        """
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        save_file = os.path.join(save_path, save_file_path)
        np.save(save_file, results)
        self.log_message(f"Results saved to {save_file}")


