'''module uses threads to download file from s3 and generates md5 hash'''
import sys
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Manager, Process
from signal import SIGCHLD, signal
from typing import Any

from mypy_boto3_s3 import S3Client
from setproctitle import setproctitle

from .consumer import consumer
from .logger import logger
from .s3_file import S3FileHelper

setproctitle('s3-md5: main process')


def consumer_death_strategy(signal_number: int, stack: Any, process: Process, thread_executor: ThreadPoolExecutor):
    '''handler to call when consumer process dies'''
    logger.error(f"consumer died with {signal_number}")
    logger.error(f"consumer stack {stack}")
    logger.warning("will exit")
    process.terminate()
    thread_executor.shutdown(wait=False, cancel_futures=True)
    sys.exit(1)


def parse_file_md5(s3_client: S3Client,
                   bucket: str,
                   file_name: str,
                   chunk_size: int,
                   workers: int) -> str:
    '''main function to orchestrate the md5 generation of s3 object'''
    s3_file = S3FileHelper(s3_client, bucket, file_name)

    file_size = s3_file.get_file_size()
    logger.info(f"file size {file_size} bytes")
    if file_size < chunk_size:
        chunk_size = file_size
    logger.info(f"chunk size {chunk_size} bytes")

    chunk_count = file_size // chunk_size
    logger.debug(f"chunk count {chunk_count}")

    if chunk_count < workers:
        workers = chunk_count
    logger.info(f"workers {workers}")

    md5_store = Manager().Value(str, '')
    byte_store = Manager().dict()

    consumer_process = Process(target=consumer, args=(
        byte_store, md5_store, chunk_count), name="s3-md5: sub process")
    consumer_process.start()

    with ThreadPoolExecutor(max_workers=workers) as thread_executor:
        signal(SIGCHLD, lambda signal_number, stack: consumer_death_strategy(
            signal_number, stack, consumer_process, thread_executor))

        def wrapper(part_number: int):
            ranged_bytes_string = s3_file.calculate_range_bytes_from_part_number(
                part_number, chunk_size, chunk_count)
            logger.debug(f"downloading {ranged_bytes_string}")
            ranged_bytes = s3_file.get_range_bytes(ranged_bytes_string)
            logger.debug(f"downloaded {ranged_bytes_string}")
            byte_store[part_number] = ranged_bytes
        for part_number in range(chunk_count):
            try:
                thread_executor.submit(wrapper, part_number)
            # pylint: disable=broad-exception-caught
            except Exception as exception:
                logger.error(f"parse_file_md5 {exception}")
                thread_executor.shutdown(wait=False, cancel_futures=True)
                consumer_process.terminate()
                sys.exit(1)
        thread_executor.shutdown()

    consumer_process.join()
    return md5_store.value
