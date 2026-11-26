import filetype
from pathlib import Path

from core.signatures import (
    EXTENSION_MAP,
    DANGEROUS_EXTENSIONS,
    DECOY_EXTENSIONS,
    SUSPICIOUS_UNICODE
)


def detect_file(file_path):
    path = Path(file_path)

    result = {
        "filename": path.name,
        "path": str(path),
        "declared_extension": "",
        "actual_type": "Unknown",
        "threats": [],
        "status": "Unverified"
    }

    if not path.is_file():
        result["status"] = "Error"
        result["threats"].append("Invalid file path")
        return result

    declared = path.suffix.lower().lstrip(".")
    result["declared_extension"] = declared

    # 1. Binary signature analysis

    try:
        detected = filetype.guess(str(path))

        if detected:
            actual = detected.extension
            result["actual_type"] = actual

            valid_extensions = EXTENSION_MAP.get(
                actual, {actual}
            )

            if declared not in valid_extensions:
                result["threats"].append(
                    "File extension mismatch"
                )

    except OSError:
        result["status"] = "Error"
        result["threats"].append("Unable to read file")
        return result

    # 2. Double extension detection

    extensions = [
        ext.lower().lstrip(".")
        for ext in path.suffixes
    ]

    if len(extensions) >= 2:
        if (
            extensions[-1] in DANGEROUS_EXTENSIONS
            and extensions[-2] in DECOY_EXTENSIONS
        ):
            result["threats"].append(
                "Deceptive double extension"
            )

    # 3. Hidden Unicode detection

    if any(
        char in SUSPICIOUS_UNICODE
        for char in path.name
    ):
        result["threats"].append(
            "Suspicious Unicode characters"
        )

    # Determine final status

    if result["threats"]:
        result["status"] = "Suspicious"
    elif detected:
        result["status"] = "No mismatch"

    return result
