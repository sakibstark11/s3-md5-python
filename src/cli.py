'''Cli module'''
from argparse import ArgumentParser
from multiprocessing import cpu_count


def parse_args():
    '''parses command line arguments'''
    DEFAULT_WORKERS = cpu_count() * 2 - 1
    DEFAULT_CHUNK_SIZE = 1000000

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
                        default=DEFAULT_CHUNK_SIZE,
                        help='chunk size to download on each request')
    return parser.parse_args()
