import logging
import sys
import os
import inspect
from dotenv import load_dotenv

load_dotenv()  # Load .env if present

def get_logger() -> logging.Logger:
    caller = inspect.stack()[1].frame.f_globals["__name__"]
    logger = logging.getLogger(caller)

    if not logger.handlers:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, log_level, logging.DEBUG))

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
