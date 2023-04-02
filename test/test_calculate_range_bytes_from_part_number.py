'''tests range byte calculator function'''
from typing import Tuple

from mypy_boto3_s3 import S3Client

from src.s3_file import S3FileHelper


def test_calculate_range_bytes_from_part_number(s3_setup: Tuple[S3Client, str, str, str]):
    '''test function'''
    s3_client, test_bucket, test_file_name, _ = s3_setup
    s3_file = S3FileHelper(s3_client, test_bucket, test_file_name)
    s3_file.get_file_size()
    part_number = 1
    chunk_size = 1000000
    file_chunk_count = 10
    byte_range = s3_file.calculate_range_bytes_from_part_number(
        part_number, chunk_size, file_chunk_count)
    assert byte_range == 'bytes=1000000-1999999'
