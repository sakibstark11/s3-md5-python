import aioboto3
from moto import mock_s3
from pytest import fixture


@fixture
async def s3_setup():
    with mock_s3():
        async with aioboto3.Session().client('s3', region_name='ap-east-1') as s3_client:
            test_bucket = 'bucket'
            test_file_name = 'key'
            test_body = '0123456789'

            await s3_client.create_bucket(
                Bucket=test_bucket,
                CreateBucketConfiguration={'LocationConstraint': 'ap-east-1'}
            )
            await s3_client.put_object(
                Bucket=test_bucket,
                Key=test_file_name,
                Body=test_body
            )

            yield s3_client, test_bucket, test_file_name, test_body
