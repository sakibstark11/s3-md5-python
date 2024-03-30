'''creates a logger'''
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", '%d-%m-%Y %H:%M:%S')
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
