from typing import Tuple

from moto import mock_s3
from mypy_boto3_s3 import S3Client

from s3_md5 import get_range_bytes


def test_get_range_bytes(s3_setup: Tuple[S3Client, str, str, str]):
    s3_client, test_bucket, test_file_name, test_body = s3_setup
    part_number = 1
    chunk_size = 1
    file_size = 10
    file_chunk_count = 10
    data = get_range_bytes(s3_client, test_bucket, test_file_name, part_number,
                           chunk_size, file_size, file_chunk_count)
    assert data == bytes(test_body[1], 'utf-8')
