import os


def get_full_path(path: str) -> str:
    parent_directory = os.getcwd()
    return os.path.join(parent_directory, path)


def to_hex(number: int) -> str:
    s = hex(number).split('x')[-1]
    if len(s) == 1:
        s = '0' + s
    return s
