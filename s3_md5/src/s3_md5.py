'''module uses threads to download file from s3 and generates md5 hash'''
import asyncio
import sys
from multiprocessing import Manager, Process
from signal import SIGCHLD, signal
from typing import Any

from mypy_boto3_s3 import S3Client
from setproctitle import setproctitle

from .consumer import consumer
from .logger import logger
from .s3_file import S3FileHelper
from .utils import bytes_to_mega_bytes

setproctitle('s3-md5')


def consumer_death_strategy(signal_number: int,
                            stack: Any,
                            process: Process):
    '''handler to call when consumer process dies'''
    if process.exitcode != 0:
        logger.error(
            f"consumer died with signal number {signal_number} exit code {process.exitcode}")
        logger.error(f"consumer stack {stack}")
        logger.warning("will exit")
        process.terminate()
        sys.exit(1)
    logger.debug("consumer process finished")


async def parse_file_md5(s3_client: S3Client,
                         bucket: str,
                         file_name: str,
                         chunk_size: int,
                         block_size: int):
    '''main function to orchestrate the md5 generation of s3 object'''
    s3_file = S3FileHelper(s3_client, bucket, file_name)

    file_size = await s3_file.get_file_size()
    logger.info(f"file size {bytes_to_mega_bytes(file_size)} megabyte(s)")
    if file_size < chunk_size:
        chunk_size = file_size
    logger.info(f"chunk size {bytes_to_mega_bytes(chunk_size)} megabyte(s)")

    chunk_count = file_size // chunk_size
    logger.debug(f"chunk count {chunk_count}")

    logger.info(f"block size {block_size}")

    md5_store = Manager().Value(str, '')
    byte_store = Manager().dict()
    semaphore = asyncio.Semaphore(block_size)

    consumer_process = Process(target=consumer, args=(
        byte_store, md5_store, chunk_count))
    consumer_process.start()

    signal(SIGCHLD, lambda signal_number, stack: consumer_death_strategy(
        signal_number, stack, consumer_process))

    async def wrapper(part_number: int):
        async with semaphore:
            ranged_bytes_string = s3_file.calculate_range_bytes_from_part_number(
                part_number, chunk_size, chunk_count)
            logger.debug(f"downloading {ranged_bytes_string}")
            ranged_bytes = await s3_file.get_range_bytes(ranged_bytes_string)
            logger.debug(f"downloaded {ranged_bytes_string}")
            byte_store[part_number] = ranged_bytes

    tasks = [asyncio.create_task(wrapper(part_number))
             for part_number in range(chunk_count)]
    try:
        await asyncio.gather(*tasks)
    # pylint: disable=broad-exception-caught
    except Exception as exception:
        logger.error(f"parse_file_md5 {exception}")
        consumer_process.terminate()
        sys.exit(1)

    consumer_process.join()
    return md5_store.value
