from pathlib import Path

from core.detector import detect_file
from core.risk_analyzer import analyze_risk
from database.db import save_scan


def scan_file(file_path, source="Manual"):
    # Detect file identity spoofing
    result = detect_file(file_path)

    # Perform risk assessment
    risk_result = analyze_risk(result)
    result.update(risk_result)

    # Save result to database
    result["scan_id"] = save_scan(result, source)

    return result


def scan_directory(directory_path, source="Manual"):
    directory = Path(directory_path)
    results = []

    if not directory.is_dir():
        raise ValueError("Invalid directory path")

    for path in directory.rglob("*"):
        if path.is_file() and not path.is_symlink():
            result = scan_file(path, source)
            results.append(result)

    return results
