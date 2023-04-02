'''driver'''
from time import perf_counter

from boto3 import client

from src.cli import parse_args
from src.logger import logger
from src.s3_md5 import parse_file_md5

if __name__ == '__main__':
    start_time = perf_counter()
    args = parse_args()
    main_s3_client = client('s3')
    md5_hash = parse_file_md5(
        main_s3_client,
        args.bucket,
        args.file_name,
        args.chunk_size,
        args.workers
    )
    logger.info(f'md5 hash {md5_hash}')
    logger.info(f'took {perf_counter() - start_time} seconds')
