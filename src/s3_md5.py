'''module uses threads to download file from s3 and generates md5 hash'''
from concurrent.futures import ThreadPoolExecutor
from hashlib import md5
from multiprocessing import Process, Queue, Manager
from multiprocessing.managers import ValueProxy
from typing import Type

from mypy_boto3_s3 import S3Client

from src.logger import logger

from src.s3_file import S3FileHelper


def consumer(queue: Queue, variable: ValueProxy[str]):
    '''a process that subscribes to the queue and processes md5'''
    hasher = md5()
    while True:
        item = queue.get()
        if item is None:
            break
        logger.info("consuming range")
        hasher.update(item)
    md5_hash = hasher.hexdigest()
    logger.info(md5_hash)
    variable.value = md5_hash


def process_block(block_number: int,
                  block_count: int,
                  chunk_count: int,
                  chunk_size: int,
                  chunk_count_per_block: int,
                  workers: int,
                  queue: Queue,
                  s3_file: S3FileHelper):
    '''runs individual blocks into a separate process'''
    logger.info(f"processing block {block_number}")
    start_part_number = block_number * chunk_count_per_block
    end_part_number = chunk_count - 1 if block_number == block_count - \
        1 else (start_part_number + chunk_count_per_block) - 1
    logger.info(f"part number {start_part_number}-{end_part_number}")

    with ThreadPoolExecutor(max_workers=workers) as thread_executor:
        def wrapper(part_number: int):
            ranged_bytes_string = s3_file.calculate_range_bytes_from_part_number(
                part_number, chunk_size, chunk_count)
            logger.debug(f"downloading {ranged_bytes_string}")
            ranged_bytes = s3_file.get_range_bytes(ranged_bytes_string)
            logger.debug(f"downloaded {ranged_bytes_string}")
            return ranged_bytes

        results = thread_executor.map(wrapper, range(
            start_part_number, end_part_number + 1))

        for result in results:
            queue.put(result)


def parse_file_md5(s3_client: S3Client,
                   bucket: str,
                   file_name: str,
                   chunk_size: int,
                   workers: int) -> str:
    '''main function to orchestrate the md5 generation of s3 object'''
    s3_file = S3FileHelper(s3_client, bucket, file_name)

    file_size = s3_file.get_file_size()
    if file_size < chunk_size:
        raise AssertionError('file size cannot be smaller than chunk size')
    logger.info(f'file size {file_size} bytes')
    logger.info(f'chunk size {chunk_size} bytes')
    logger.info(f'workers {workers}')

    chunk_count = file_size // chunk_size
    logger.info(f'chunk count {chunk_count}')

    if chunk_count < workers:
        raise AssertionError('chunk count cannot be smaller than workers')

    block_count = chunk_count // workers
    logger.info(f'block count {block_count}')

    chunk_count_per_block = chunk_count // block_count
    logger.info(f'chunk to get per block {chunk_count_per_block}')

    queue = Queue()
    variable = Manager().Value(str, None)

    consumer_process = Process(target=consumer, args=(queue, variable))
    consumer_process.start()

    for block_number in range(0, block_count):
        process_block(block_number, block_count, chunk_count,
                      chunk_size, chunk_count_per_block, workers // 2, queue, s3_file)
    queue.put(None)
    consumer_process.join()
    return variable.value
