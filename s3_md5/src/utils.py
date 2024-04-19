'''basic converter utilities'''


def bytes_to_mega_bytes(value: int) -> float:
    '''convert bytes to megabytes'''
    return value / (1024 * 1024)


def seconds_to_minutes(value: float) -> float:
    '''convert seconds to minutes'''
    return value / 60
