import os
from dotenv import dotenv_values
import logging

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
    def __init__(self):
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
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def _load_logging(self, log_file: str='base_endpoints.log') -> None:
        """
        Initialize logging for the endpoint interactions.
        Logs will be written to the specified log file.
        """
        logging.basicConfig(filename=log_file, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def log_message(self, message: str) -> None:
        """
        Log a message to the logger.
        """
        self.logger.log(logging.INFO, message)

    @abstractmethod
    def query(self, prompt: str, model_type: Type[T], model_name: str, **kwargs) -> tuple:
        """
        Query the LLM endpoint with a given prompt and model name.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    @abstractmethod
    def query_with_retries(self, prompt: str, model_type: Type[T], model_name: str, **kwargs) -> tuple:
        """
        Query the LLM endpoint with retry logic.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    @abstractmethod
    def query_batch(self, prompts: str, model_type: Type[T], model_name: str, **kwargs) -> list[tuple]:
        """
        Query the LLM endpoint with a batch of prompts.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("This method should be overridden by subclasses")


