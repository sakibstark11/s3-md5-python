'''S3 file helper module'''
from mypy_boto3_s3 import S3Client


class S3FileHelper:
    '''A helper class to call actions on an s3 file'''
    __file_size: int

    def __init__(self, s3_client: S3Client, bucket: str, file_name: str) -> None:
        self.s3_client = s3_client
        self.bucket = bucket
        self.file_name = file_name

    def get_file_size(self) -> int:
        '''makes a head object request to get file size in bytes'''
        s3_object = self.s3_client.head_object(Bucket=self.bucket,
                                               Key=self.file_name)
        self.__file_size = s3_object['ContentLength']
        return self.__file_size

    def calculate_range_bytes_from_part_number(self, part_number: int,
                                               chunk_size: int,
                                               file_chunk_count: int) -> str:
        '''
            calculates the byte range to fetch
            starts from 0 if its the first iteration
            if not the first iteration; part number * chunk size
            uses remaining file length if its the last iteration
            if not; (( part number * chunk size ) + chunk size ) - 1
        '''
        start_bytes: int = (
            part_number * chunk_size) if part_number != 0 else 0

        end_bytes: int = self.__file_size if part_number + \
            1 == file_chunk_count else (((part_number * chunk_size) + chunk_size) - 1)
        return f'bytes={start_bytes}-{end_bytes}'

    def get_range_bytes(self, range_string: str) -> bytes:
        '''fetches the range bytes requested from s3'''
        return self.s3_client.get_object(Bucket=self.bucket,
                                         Key=self.file_name,
                                         Range=range_string)['Body'].read()
