'''common resource for testing'''
from boto3 import client
from moto import mock_s3
from pytest import fixture


@fixture
def s3_setup():
    with mock_s3():
        s3_client = client('s3')
        test_bucket = 'bucket'
        test_file_name = 'key'
        test_body = '0123456789'
        s3_client.create_bucket(Bucket=test_bucket)
        s3_client.put_object(Bucket=test_bucket,
                             Key=test_file_name,
                             Body=test_body)
        yield s3_client, test_bucket, test_file_name, test_body
