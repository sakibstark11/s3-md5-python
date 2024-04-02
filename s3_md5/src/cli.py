'''Cli module'''
from argparse import ArgumentParser
from multiprocessing import cpu_count

from speedtest import Speedtest

from .logger import logger

DEFAULT_WORKERS = cpu_count() * 2 - 1
BIT_IN_BYTE = 0.125
DEFAULT_CHUNK_SIZE = 1000000


def get_download_speed():
    '''uses speed test to get download speed'''
    logger.info("picking chunk size")
    try:
        speed_test = Speedtest()
        download_speed = speed_test.download(threads=1)
        chunk_size = int(download_speed * BIT_IN_BYTE)
        return chunk_size
    # pylint: disable=broad-exception-caught
    except Exception as exception:
        logger.debug(f"get_download_speed {exception}")
        logger.warning(
            "will use default chunk size as automatic chunk size calculation failed")
        return DEFAULT_CHUNK_SIZE


def parse_args():
    '''parses command line arguments'''
    parser = ArgumentParser(description='parse md5 of an s3 object')
    parser.add_argument('bucket',
                        type=str,
                        help='bucket name')
    parser.add_argument('file_name',
                        help='file name',
                        type=str)
    parser.add_argument('-c', '--chunk_size', type=int,
                        default=None,
                        help='chunk size to download on each request')
    parsed_args = parser.parse_args()
    if parsed_args.chunk_size is None:
        parsed_args.chunk_size = get_download_speed()
    return parsed_args
