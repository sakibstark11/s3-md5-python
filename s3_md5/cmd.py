'''driver'''
from time import perf_counter

from boto3 import client

from s3_md5.src.cli import parse_args
from s3_md5.src.logger import logger
from s3_md5.src.s3_md5 import parse_file_md5


def run():
    '''runs the script'''
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


if __name__ == "__main__":
    run()
