import logging
import os

from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())


def get_logger(module_name: str) -> logging.Logger:
    logger = logging.getLogger(module_name)
    log_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    log_level = os.getenv("LOGLEVEL", "INFO")

    logger.setLevel(log_level)

    return logger
