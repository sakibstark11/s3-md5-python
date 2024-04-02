'''creates a logger'''
import logging
import os
import sys

LOG_LEVELS = {
    'CRITICAL': logging.CRITICAL,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO
}
logger = logging.getLogger(__name__)
log_level = LOG_LEVELS[os.getenv('LOG_LEVEL', 'INFO')]
logger.setLevel(log_level)

stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", '%d-%m-%Y %H:%M:%S')
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
