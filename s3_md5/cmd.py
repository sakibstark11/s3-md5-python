'''driver'''
from asyncio import run as asyncio_run
from time import perf_counter

from aioboto3 import Session

from s3_md5.src.cli import parse_args
from s3_md5.src.logger import logger
from s3_md5.src.s3_md5 import parse_file_md5
from s3_md5.src.utils import seconds_to_minutes


async def run():
    '''runs the script'''
    start_time = perf_counter()
    args = parse_args()
    main_s3_session = Session()
    async with main_s3_session.client('s3') as s3_client:
        md5_hash = await parse_file_md5(
            s3_client,
            args.bucket,
            args.file_name,
            args.chunk_size,
            args.block_size
        )
        logger.info(f"md5 hash {md5_hash}")
        logger.info(
            f"took {seconds_to_minutes(perf_counter() - start_time)} minute(s)")


if __name__ == "__main__":
    asyncio_run(run())
