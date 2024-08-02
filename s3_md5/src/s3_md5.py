import asyncio
import sys
from multiprocessing import Manager, Process
from signal import SIGCHLD, signal
from typing import Any

from mypy_boto3_s3 import S3Client
from setproctitle import setproctitle
from tqdm import tqdm

from .consumer import consumer
from .logger import logger
from .s3_file import S3FileHelper
from .utils import bytes_to_mega_bytes

setproctitle('s3-md5')


def consumer_death_strategy(signal_number: int,
                            stack: Any,
                            process: Process):
    '''Handler to call when consumer process dies'''
    if process.exitcode != 0:
        logger.error(
            f"Consumer died with signal number {signal_number} exit code {process.exitcode}")
        logger.error(f"Consumer stack {stack}")
        logger.warning("Will exit")
        process.terminate()
        sys.exit(1)
    logger.debug("Consumer process finished")


async def parse_file_md5(s3_client: S3Client,
                         bucket: str,
                         file_name: str,
                         chunk_size: int,
                         block_size: int):
    '''Main function to orchestrate the MD5 generation of S3 object'''
    s3_file = S3FileHelper(s3_client, bucket, file_name)

    file_size = await s3_file.get_file_size()
    logger.info(f"File size {bytes_to_mega_bytes(file_size)} megabyte(s)")
    if file_size < chunk_size:
        chunk_size = file_size
    logger.info(f"Chunk size {bytes_to_mega_bytes(chunk_size)} megabyte(s)")

    chunk_count = file_size // chunk_size
    logger.info(f"Chunk count {chunk_count}")

    logger.info(f"Block size {block_size}")

    md5_store = Manager().Value(str, '')
    byte_store = Manager().dict()
    semaphore = asyncio.Semaphore(block_size)

    consumer_process = Process(target=consumer, args=(
        byte_store, md5_store, chunk_count))
    consumer_process.start()

    signal(SIGCHLD, lambda signal_number, stack: consumer_death_strategy(
        signal_number, stack, consumer_process))

    with tqdm(total=chunk_count, position=0, desc="downloaded") as progress_bar:
        async with asyncio.TaskGroup() as task_group:
            async def wrapper(part_number: int):
                ranged_bytes_string = s3_file.calculate_range_bytes_from_part_number(
                    part_number, chunk_size, chunk_count)
                async with semaphore:
                    logger.debug(
                        f"Downloading {part_number + 1} {ranged_bytes_string}")
                    ranged_bytes = await s3_file.get_range_bytes(ranged_bytes_string)
                    logger.debug(
                        f"Downloaded {part_number + 1} {ranged_bytes_string}")
                    progress_bar.update(1)
                    byte_store[part_number] = ranged_bytes

            # Process tasks in blocks
            for i in range(0, chunk_count, block_size):
                block_end = min(i + block_size, chunk_count)
                for part_number in range(i, block_end):
                    task_group.create_task(wrapper(part_number))

    consumer_process.join()
    return md5_store.value
