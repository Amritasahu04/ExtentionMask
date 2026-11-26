from pathlib import Path

from core.detector import detect_file
from core.risk_analyzer import analyze_risk


def scan_file(file_path):
    result = detect_file(file_path)

    # Perform risk assessment
    risk_result = analyze_risk(result)

    # Combine detection and risk analysis results
    result.update(risk_result)

    return result


def scan_directory(directory_path):
    directory = Path(directory_path)
    results = []

    if not directory.is_dir():
        raise ValueError("Invalid directory path")

    for path in directory.rglob("*"):
        if path.is_file() and not path.is_symlink():
            result = scan_file(path)
            results.append(result)

    return results
