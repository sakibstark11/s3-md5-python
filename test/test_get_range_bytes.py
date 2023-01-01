from boto3 import client
from moto import mock_s3

from s3_md5 import get_range_bytes


@mock_s3
def test_get_range_bytes():
    s3_client = client('s3')
    test_bucket = 'bucket'
    test_key = 'key'
    test_body = '0123456789'
    part_number = 1
    chunk_size = 1
    file_size = 10
    file_chunk_count = 10
    s3_client.create_bucket(Bucket=test_bucket)
    s3_client.put_object(Bucket=test_bucket, Key=test_key, Body=test_body)
    data = get_range_bytes(s3_client, test_bucket, test_key, part_number,
                           chunk_size, file_size, file_chunk_count)
    assert data == b'1'
