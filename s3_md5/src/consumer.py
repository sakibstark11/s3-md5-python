import sys
from hashlib import md5
from multiprocessing.managers import ValueProxy
from typing import Dict

from tqdm import tqdm

from .logger import logger


def consumer(store: Dict[int, bytes], variable: ValueProxy[str], chunk_count: int):
    '''a process that subscribes to the queue and processes md5'''
    hasher = md5()
    logger.debug("consumer started")
    element_to_consume = 0
    with tqdm(total=chunk_count) as progress_bar:
        while element_to_consume < chunk_count:
            try:
                potential_item = store.get(element_to_consume)
                if potential_item is not None:
                    hasher.update(potential_item)
                    logger.debug(
                        f"consumed chunk {element_to_consume}"
                        + " " +
                        f"left {chunk_count - element_to_consume + 1}")
                    element_to_consume += 1
                    progress_bar.update(1)
            # pylint: disable=broad-exception-caught
            except Exception as exception:
                logger.error(f"consumer {exception}")
                sys.exit(1)

        logger.debug("calculating md5 hash")
        md5_hash = hasher.hexdigest()
        variable.value = md5_hash
        sys.exit()
