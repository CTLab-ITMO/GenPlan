import os


def get_full_path(path: str) -> str:
    parent_directory = os.path.abspath(os.path.join(os.getcwd(), '..'))
    return os.path.join(parent_directory, path)
