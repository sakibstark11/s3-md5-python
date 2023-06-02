'''module uses threads to download file from s3 and generates md5 hash'''
from concurrent.futures import ThreadPoolExecutor
from os import remove

from mypy_boto3_s3 import S3Client

from src.logger import logger
from src.s3_file import S3FileHelper
from src.resume import load_state, save_state


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

    chunk_count = file_size // chunk_size
    logger.info(f'chunk count {chunk_count}')

    if chunk_count < workers:
        raise AssertionError('chunk size too large')

    block_count = chunk_count // workers
    logger.info(f'block count {block_count}')

    chunk_count_per_block = chunk_count // block_count
    logger.info(f'chunk to get per block {chunk_count_per_block}')

    start_block, hash_object = load_state()
    if start_block != 0:
        logger.info(f"resuming from block {start_block}")

    for block_number in range(start_block, block_count):
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

            for result in thread_executor.map(wrapper,
                                              range(start_part_number, end_part_number + 1)):
                hash_object.update(result)
            save_state(block_number, hash_object)

    remove('.state.block')
    remove('.state.pickle')

    return hash_object.hexdigest()
