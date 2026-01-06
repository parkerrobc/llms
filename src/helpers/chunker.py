from typing import Iterator


def chunk_file(file_path: str, chunk_size: int, overlap: int) -> Iterator[str]:
    curr: str = ''

    for line in read_file(file_path):
        curr += line

        while curr and len(curr) > chunk_size:
            yield curr[:chunk_size]
            curr = curr[chunk_size - overlap:]

    yield curr


def read_file(file_path: str) -> Iterator[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            yield line
