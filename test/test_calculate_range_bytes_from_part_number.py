from s3_md5 import calculate_range_bytes_from_part_number


def test_calculate_range_bytes_from_part_number():
    part_number = 1
    chunk_size = 1000000
    file_size = 10000000
    file_chunk_count = 10
    range = calculate_range_bytes_from_part_number(
        part_number, chunk_size, file_size, file_chunk_count)
    assert range == "bytes=1000000-1999999"
