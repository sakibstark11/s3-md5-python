'''module uses threads to download file from s3 and generates md5 hash'''
import asyncio
import sys
from hashlib import md5

from mypy_boto3_s3 import S3Client
from setproctitle import setproctitle
from tqdm import tqdm

from .logger import logger
from .s3_file import S3FileHelper
from .utils import bytes_to_mega_bytes

setproctitle('s3-md5')


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

    md5_store = md5()
    byte_store = {}
    next_ingest_part_number = 0
    progress_bar = tqdm(total=chunk_count)
    semaphore = asyncio.Semaphore(block_size)

    async def wrapper(part_number: int):
        async with semaphore:
            ranged_bytes_string = s3_file.calculate_range_bytes_from_part_number(
                part_number, chunk_size, chunk_count)
            logger.debug(f"downloading {ranged_bytes_string}")
            ranged_bytes = await s3_file.get_range_bytes(ranged_bytes_string)
            logger.debug(f"downloaded {ranged_bytes_string}")
            byte_store[part_number] = ranged_bytes

            nonlocal next_ingest_part_number
            while next_ingest_part_number < chunk_count:
                logger.debug(f"checking {next_ingest_part_number}")
                potential_bytes = byte_store.get(next_ingest_part_number)
                if potential_bytes is None:
                    logger.debug(
                        f"expected part number {next_ingest_part_number} not available")
                    break
                md5_store.update(potential_bytes)
                progress_bar.update(1)
                logger.debug(f"ingested {next_ingest_part_number}")
                del byte_store[next_ingest_part_number]
                next_ingest_part_number += 1

    tasks = [asyncio.create_task(wrapper(part_number))
             for part_number in range(chunk_count)]
    try:
        await asyncio.gather(*tasks)
    # pylint: disable=broad-exception-caught
    except Exception as exception:
        logger.error(f"parse_file_md5 {exception}")
        sys.exit(1)

    return md5_store.hexdigest()
