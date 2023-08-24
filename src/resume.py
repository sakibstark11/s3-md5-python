"""
This module is responsible for loading the state of the hashing process.
"""
import pickle
from typing import Tuple
from src.logger import logger
import rehash


def load_state() -> Tuple[int, rehash.ResumableHasher]:
    '''try and load existing state'''
    try:
        with open('.state.block', 'r',  encoding='utf-8') as previous_block_number, \
                open('.state.pickle', 'rb') as previous_hash:

            hash_object = pickle.load(previous_hash)
            start_block = int(previous_block_number.read()) + 1
            return start_block, hash_object
    except FileNotFoundError:
        return 0, rehash.new('md5')


def save_state(block_number: int, hash_object: rehash.ResumableHasher) -> None:
    '''try and save state'''
    try:
        with open('.state.block', 'w',  encoding='utf-8') as current_block_number, \
                open('.state.pickle', 'wb') as current_hash:
            pickle.dump(hash_object, current_hash)
            current_block_number.write(str(block_number))

    except OSError as exception:
        raise OSError('Could not save state') from exception
