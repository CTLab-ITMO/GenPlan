import os


def get_full_path(path: str) -> str:
    parent_directory = os.getcwd()
    return os.path.join(parent_directory, path)
