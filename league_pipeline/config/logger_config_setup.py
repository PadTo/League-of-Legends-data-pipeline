import logging
import json
import logging.config
from pathlib import Path

def logging_setup(config_name: str, logger_name: str) -> logging.Logger:
    """
    Sets up and configures the logging module using a JSON config file.

    Args:
        config_path (str): Path to the logging configuration file.

    Returns:
        logging.Logger: Configured logger instance.
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

