import os


def relative_path(file: str, *path: str) -> str:
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(file)))
    return os.path.join(location, *path)
