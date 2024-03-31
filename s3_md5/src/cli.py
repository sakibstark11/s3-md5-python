'''Cli module'''
from argparse import ArgumentParser
from multiprocessing import cpu_count

from speedtest import Speedtest

from .logger import logger


def parse_args():
    '''parses command line arguments'''
    DEFAULT_WORKERS = cpu_count() * 2 - 1
    BIT_IN_BYTE = 0.125

    parser = ArgumentParser(description='parse md5 of an s3 object')
    parser.add_argument('bucket',
                        type=str,
                        help='bucket name')
    parser.add_argument('file_name',
                        help='file name',
                        type=str)
    parser.add_argument('-w', '--workers', type=int,
                        default=DEFAULT_WORKERS,
                        help='number of cpu threads to use for downloading')
    parser.add_argument('-c', '--chunk_size', type=int,
                        default=None,
                        help='chunk size to download on each request')
    parsed_args = parser.parse_args()
    if parsed_args.chunk_size is None:
        logger.info("picking chunk size")
        speed_test = Speedtest()
        parsed_args.chunk_size = int(
            speed_test.download() * BIT_IN_BYTE) // parsed_args.workers
    return parsed_args
