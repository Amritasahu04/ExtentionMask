from pathlib import Path
from collections import Counter

from core.scanner import scan_file, scan_directory


def display_result(result):
    print("-" * 50)
    print("Filename:", result["filename"])
    print("Declared Extension:", result["declared_extension"])
    print("Actual File Type:", result["actual_type"])
    print("Status:", result["status"])

    score = result["risk_score"]

    print(
        "Risk Score:",
        f"{score}/100" if score is not None else "Unknown"
    )

    print("Severity:", result["severity"])

    if result["risk_reasons"]:
        print("Security Findings:")

        for reason in result["risk_reasons"]:
            print(" -", reason)


def display_summary(results):
    counts = Counter(
        result["severity"] for result in results
    )

    print("\n" + "=" * 50)
    print("SECURITY SCAN SUMMARY")
    print("=" * 50)

    print("Total Files Scanned:", len(results))
    print("No Identified Risk:", counts["None"])
    print("Low Risk:", counts["Low"])
    print("Medium Risk:", counts["Medium"])
    print("High Risk:", counts["High"])
    print("Critical Risk:", counts["Critical"])
    print("Unknown:", counts["Unknown"])


def main():
    print("=" * 50)
    print("EXTENSIONMASK - File Security Scanner")
    print("=" * 50)

    path = input("Enter file or directory path: ")
    path = Path(path.strip().strip('"'))

    if path.is_file():
        display_result(scan_file(path))

    elif path.is_dir():
        results = scan_directory(path)

        for result in results:
            display_result(result)

        display_summary(results)

    else:
        print("Invalid path!")


if __name__ == "__main__":
    main()
from pathlib import Path
from collections import Counter

from core.scanner import scan_file, scan_directory


def display_result(result):
    print("-" * 50)
    print("Filename:", result["filename"])
    print("Declared Extension:", result["declared_extension"])
    print("Actual File Type:", result["actual_type"])
    print("Status:", result["status"])

    score = result["risk_score"]

    print(
        "Risk Score:",
        f"{score}/100" if score is not None else "Unknown"
    )

    print("Severity:", result["severity"])

    if result["risk_reasons"]:
        print("Security Findings:")

        for reason in result["risk_reasons"]:
            print(" -", reason)


def display_summary(results):
    counts = Counter(
        result["severity"] for result in results
    )

    print("\n" + "=" * 50)
    print("SECURITY SCAN SUMMARY")
    print("=" * 50)

    print("Total Files Scanned:", len(results))
    print("No Identified Risk:", counts["None"])
    print("Low Risk:", counts["Low"])
    print("Medium Risk:", counts["Medium"])
    print("High Risk:", counts["High"])
    print("Critical Risk:", counts["Critical"])
    print("Unknown:", counts["Unknown"])


def main():
    print("=" * 50)
    print("EXTENSIONMASK - File Security Scanner")
    print("=" * 50)

    path = input("Enter file or directory path: ")
    path = Path(path.strip().strip('"'))

    if path.is_file():
        display_result(scan_file(path))

    elif path.is_dir():
        results = scan_directory(path)

        for result in results:
            display_result(result)

        display_summary(results)

    else:
        print("Invalid path!")


if __name__ == "__main__":
    main()
