'''module uses threads to download file from s3 and generates md5 hash'''
from concurrent.futures import ThreadPoolExecutor
from hashlib import md5
from multiprocessing import Process, Queue

from mypy_boto3_s3 import S3Client

from src.logger import logger
from src.s3_file import S3FileHelper


def consumer(queue: Queue):
    hash_object = md5()
    print('Consumer: Running', flush=True)
    # consume work
    while True:
        # get a unit of work
        item = queue.get()
        # check for stop
        if item is None:
            break
        # report
        print(f'>got {item}', flush=True)
    # all done
    print('Consumer: Done', flush=True)


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
    file_chunk_count = file_size // chunk_size
    logger.info(f'file chunk count {file_chunk_count}')

    with ThreadPoolExecutor(max_workers=workers) as thread_executor:
        def wrapper(part_number: int):
            ranged_bytes_string = s3_file.calculate_range_bytes_from_part_number(
                part_number, chunk_size, file_chunk_count)
            logger.info(f"downloading {ranged_bytes_string}")
            ranged_bytes = s3_file.get_range_bytes(ranged_bytes_string)
            logger.info(f"downloaded {ranged_bytes_string}")
            return ranged_bytes

        queue = Queue()
        consumer_process = Process(target=consumer, args=(queue,))

        logger.info('downloading file')
        for part_number in range(file_chunk_count):
            future = thread_executor.submit(wrapper,
                                            part_number)
            queue.put(future)

        queue.put(None)
