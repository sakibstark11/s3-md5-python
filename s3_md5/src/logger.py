'''creates a logger'''
import logging
import os
import sys

levels = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG
}
logger = logging.getLogger(__name__)
logger.setLevel(levels.get(os.getenv('LOG_LEVEL', None), logging.INFO))

stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", '%d-%m-%Y %H:%M:%S')
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
