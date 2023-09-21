import logging
from typing import Optional
from logging import Logger
from typing import List, Dict, Union, Callable, Optional, Any, Generator
import json

def setup_logger(name: str, level: int = logging.INFO, log_file_path: Optional[str] = None) -> Logger:
    """
    Setup a logger with the specified name, level, and optional log file.
    
    Parameters:
    - name (str): The name of the logger
    - level (int): The logging level (default: logging.INFO)
    - log_file_path (str): The path to the log file (default: None, logs to stdout)
    
    Returns:
    - Logger: Configured logger object
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove all handlers to avoid duplicate logs in this environment
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create a file handler if log_file_path is provided
    if log_file_path:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        # Create console handler with a higher log level
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger