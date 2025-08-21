import logging
import json
import logging.config
from pathlib import Path

def logging_setup(config_name: str, logger_name: str) -> logging.Logger:
    """
    Set up and configure the logging module using a JSON config file.

    This function reads a JSON logging configuration file from the same directory
    as this module and configures the Python logging system accordingly.

    Args:
        config_name (str): Name of the JSON configuration file (e.g., "log_config.json").
        logger_name (str): Name identifier for the logger instance to create.

    Returns:
        logging.Logger: Configured logger instance ready for use.

    Raises:
        FileNotFoundError: If the specified config file doesn't exist.
        json.JSONDecodeError: If the config file contains invalid JSON.
        ValueError: If the config file has invalid logging configuration.
        Exception: For any other configuration-related errors.

    Example:
        >>> logger = logging_setup("log_config.json", "my_pipeline")
        >>> logger.info("Logger initialized successfully")
    """

    try:
        config_path = Path(__file__).parent / config_name 
        
        with open(config_path, "r") as f_in:
            config = json.load(f_in)

    except Exception as e:
        raise

    logging.config.dictConfig(config)
    logger = logging.getLogger(logger_name)
    logger.info("Logger Initialized")

    return logger

