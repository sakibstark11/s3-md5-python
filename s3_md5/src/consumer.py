from hashlib import md5
from multiprocessing.managers import DictProxy, ValueProxy

from .logger import logger


def consumer(store: DictProxy, variable: ValueProxy[str], chunk_count: int):
    '''a process that subscribes to the queue and processes md5'''
    hasher = md5()
    logger.info("consumer started")
    element_to_consume = 0
    while element_to_consume < chunk_count:
        potential_item = store.get(element_to_consume)
        if potential_item is not None:
            hasher.update(potential_item)
            logger.info(
                f"consumed chunk {element_to_consume}")
            logger.info(
                f"remaining chunk {chunk_count - (element_to_consume + 1)}")
            element_to_consume += 1
    logger.info("calculating md5 hash")
    md5_hash = hasher.hexdigest()
    variable.value = md5_hash
