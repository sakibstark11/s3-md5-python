import argparse
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from hashlib import md5
from time import perf_counter

import boto3
from mypy_boto3_s3 import S3Client


def get_file_size(client: S3Client,
                  bucket: str,
                  file_name: str,
                  ) -> int:
    s3_object = client.head_object(Bucket=bucket,
                                   Key=file_name)
    return s3_object['ContentLength']


def download_ranged_bytes(client: S3Client,
                          bucket: str,
                          file_name: str,
                          part_number: int,
                          chunk_size: int,
                          file_size: int,
                          file_chunk_count: int) -> bytes:
    # start from 0 if its the first iteration
    # if not first iteration part number * chunk size
    start_bytes: int = (part_number * chunk_size) if part_number != 0 else 0
    # use remaining file length if its the last iteration
    # if not (( part number * chunk size ) + chunk size ) - 1
    end_bytes: int = file_size if part_number + \
        1 == file_chunk_count else (((part_number * chunk_size) + chunk_size) - 1)

    range_string = f"bytes={start_bytes}-{end_bytes}"
    print(f"part number {part_number + 1} downloading bytes {range_string}")

    body = client.get_object(Bucket=bucket,
                             Key=file_name,
                             Range=range_string)['Body'].read()
    return body


def parse_file_md5(bucket: str,
                   file_name: str,
                   chunk_size: int,
                   workers: int) -> str:

    client: S3Client = boto3.client('s3')

    file_size = get_file_size(client, bucket, file_name)

    if file_size < chunk_size:
        raise AssertionError('file size cannot be smaller than chunk size')

    print(f"file size {file_size}")

    file_chunk_count = file_size // chunk_size
    print(f"file chunk count {file_chunk_count}")

    with ThreadPoolExecutor(max_workers=workers) as thread_executor:
        results = thread_executor.map(
            lambda part_number: download_ranged_bytes(
                client,
                bucket,
                file_name,
                part_number,
                chunk_size,
                file_size,
                file_chunk_count),
            range(file_chunk_count))

        hash_object = md5()

        for result in results:
            hash_object.update(result)

        return hash_object.hexdigest()


def parse_args():
    DEFAULT_WORKERS = multiprocessing.cpu_count() * 2 - 1
    DEFAULT_CHUNK_SIZE = 1000000

    parser = argparse.ArgumentParser(description='parse md5 of an s3 object')
    parser.add_argument('bucket',
                        type=str,
                        help='bucket name')
    parser.add_argument('file_name',
                        help="file name",
                        type=str)
    parser.add_argument("-w", "--workers", type=int,
                        default=DEFAULT_WORKERS,
                        help="number of cpu threads to use for downloading")
    parser.add_argument("-c", "--chunk_size", type=int,
                        default=DEFAULT_CHUNK_SIZE,
                        help="chunk size to download on each request")
    return parser.parse_args()


if __name__ == "__main__":
    start_time = perf_counter()

    args = parse_args()

    md5_hash = parse_file_md5(
        args.bucket,
        args.file_name,
        args.chunk_size,
        args.workers
    )
    print(f"md5 hash: {md5_hash}")

    print(f"took {perf_counter() - start_time} seconds")
