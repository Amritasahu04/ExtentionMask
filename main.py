from pathlib import Path
from core.scanner import scan_file, scan_directory


def display_result(result):
    print("-" * 50)
    print("Filename:", result["filename"])
    print("Declared Extension:", result["declared_extension"])
    print("Actual File Type:", result["actual_type"])
    print("Status:", result["status"])

    if result["threats"]:
        print("Findings:")

        for threat in result["threats"]:
            print(" -", threat)


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

        print("\nTotal files scanned:", len(results))

    else:
        print("Invalid path!")


if __name__ == "__main__":
    main()
