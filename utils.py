import numpy as np
import time
from functools import wraps
import logging


class CustomFormatter(logging.Formatter):
    """
    Formatter used on stream log-messages.
    Adds colors to messages.
    ----------------------------------
    Usage:
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    """
    purple = '\x1b[35;20m'
    green = '\x1b[32;20m'
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(levelname)s : %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: purple + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)



def generate_logger(log_path):
    """
    Generate a logger.
    ----------------------------------
    Usage:
    logger = generate_logger(log_path)
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s:%(levelname)s:%(message)s (%(filename)s:%(lineno)d)'))
    file_handler.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(CustomFormatter())

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

logger = generate_logger("./logs/segmenter_logs.txt")


def timeit(func):
    """
    Decorator used to time a function.
    ----------------------------------
    Usage:
    @timeit
    """
    @wraps(func)
    def timed(*args, **kw):
        ts = time.time()
        result = func(*args, **kw)
        te = time.time()        
        logger.info(f"Time to compute '{func.__name__}': {np.round((te - ts),2)} sec.")
        return result    
    return timed