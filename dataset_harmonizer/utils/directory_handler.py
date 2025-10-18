import os

def create_directory(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

    return os.path.abspath(path)

def check_existing_file(path: str) -> bool:
    return os.path.exists(path) and os.path.isfile(path)

def create_path(directory: str, file_name: str) -> str:
    dir_path = create_directory(directory)
    return os.path.join(dir_path, file_name)