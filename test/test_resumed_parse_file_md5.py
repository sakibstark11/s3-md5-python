'''tests the driver function'''
from hashlib import md5
from pickle import dump
from typing import Tuple

from mypy_boto3_s3 import S3Client
from rehash import new

from src.s3_md5 import parse_file_md5


def test_resumed_parse_file_md5(s3_setup: Tuple[S3Client, str, str, str]):
    '''test function'''
    s3_client, test_bucket, test_file_name, test_body = s3_setup

    with open('.state.block', 'w', encoding="utf-8") as previous_block_number:
        previous_block_number.write('1')

    hash_object = new('md5')
    hash_object.update(bytes(test_body[0:2], 'utf-8'))

    with open('.state.pickle', 'wb') as previous_md5_hash:
        dump(hash_object, previous_md5_hash)

    md5_hash = parse_file_md5(s3_client, test_bucket, test_file_name, 1, 1)
    assert md5_hash == md5(bytes(test_body, 'utf-8')).hexdigest()
