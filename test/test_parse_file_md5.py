from hashlib import md5
from typing import Tuple

from moto import mock_s3
from mypy_boto3_s3 import S3Client

from s3_md5 import parse_file_md5


def test_get_range_bytes(s3_setup: Tuple[S3Client, str, str, str]):
    s3_client, test_bucket, test_file_name, test_body = s3_setup
    md5_hash = parse_file_md5(s3_client, test_bucket, test_file_name, 1, 1)
    assert md5_hash == md5(bytes(test_body, 'utf-8')).hexdigest()
