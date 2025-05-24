import os
from dotenv import dotenv_values
import logging

class BaseEndpoint:
    """
    Base class to interact with a specific LLM endpoint.
    This class should be extended for each specific LLM endpoint.
    """
    def __init__():
        """
        Initialize the BaseEndpoint class.
        This method should be overridden by subclasses to set up the specific endpoint.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def _find_dotenv(self, start_path='.'):
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

    def load_env(self):
        """
        Load environment variables from the .env file.
        Raises FileNotFoundError if the .env file is not found.
        """
        dotenv_path = self._find_dotenv()
        if dotenv_path:
            return dotenv_values(dotenv_path)
        else:
            raise FileNotFoundError(".env file not found in any parent directory")

    def initialize_clients(self, secrets):
        """
        Initialize the clients for the specific LLM endpoint.
        This method should be overridden by subclasses to set up the specific clients.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def _load_logging(self, log_file='base_endpoints.log'):
        """
        Initialize logging for the endpoint interactions.
        Logs will be written to the specified log file.
        """
        logging.basicConfig(filename=log_file, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def log_message(self, message):
        """
        Log a message to the logger.
        """
        self.logger.log(logging.INFO, message)

    def query(self, prompt, model_name, **kwargs):
        """
        Query the LLM endpoint with a given prompt and model name.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def query_with_retries(self, prompt, model_name, **kwargs):
        """
        Query the LLM endpoint with retry logic.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def query_batch(self, prompts, model_name, **kwargs):
        """
        Query the LLM endpoint with a batch of prompts.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("This method should be overridden by subclasses")


