import logging
import json
import logging.config


def logging_setup(config_path):
    """
    Sets up and configures the logging module using a JSON config file.

    Args:
        config_path (str or Path): Path to the logging configuration file.

    Returns:
        logging.Logger: Configured logger instance.
    """

    with open(config_path) as f_in:
        config = json.load(f_in)

    logging.config.dictConfig(config)
