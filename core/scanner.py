from pathlib import Path
from core.detector import detect_file


def scan_file(file_path):
    return detect_file(file_path)


def scan_directory(directory_path):
    directory = Path(directory_path)
    results = []

    if not directory.is_dir():
        raise ValueError("Invalid directory path")

    for path in directory.rglob("*"):
        if path.is_file() and not path.is_symlink():
            result = detect_file(path)
            results.append(result)

    return results

