'''tests range fetching function'''
from typing import Tuple
from mypy_boto3_s3 import S3Client
from s3_md5.src.s3_file import S3FileHelper


def test_get_range_bytes(s3_setup: Tuple[S3Client, str, str, str]):
    '''test function'''
    s3_client, test_bucket, test_file_name, test_body = s3_setup
    s3_file = S3FileHelper(s3_client, test_bucket, test_file_name)
    s3_file.get_file_size()
    range_string = 'bytes=0-0'
    data = s3_file.get_range_bytes(range_string)
    assert data == bytes(test_body[0], 'utf-8')
