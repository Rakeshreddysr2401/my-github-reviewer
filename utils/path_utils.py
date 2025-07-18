# utils/path_utils.py

def normalize_file_path(path: str) -> str:
    """
    Normalizes a file path from a git diff.

    Removes 'a/' or 'b/' prefixes and handles /dev/null paths.

    Args:
        path (str): The file path to normalize.

    Returns:
        str: The normalized file path.
    """
    if not path or path == "/dev/null":
        return path

    # Remove 'a/' or 'b/' prefixes
    if path.startswith('a/'):
        path = path[2:]
    elif path.startswith('b/'):
        path = path[2:]

    return path
