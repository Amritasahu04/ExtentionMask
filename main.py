import time

from pathlib import Path

from core.scanner import scan_file, scan_directory
from core.monitor import DirectoryMonitor

from database.db import (
    initialize_database,
    get_scan_history,
    get_threat_history,
    get_statistics
)


def display_result(result):
    print("-" * 50)
    print("Filename:", result["filename"])
    print("Declared Extension:", result["declared_extension"])
    print("Actual File Type:", result["actual_type"])
    print("Status:", result["status"])
    print("Severity:", result["severity"])

    score = result["risk_score"]

    print(
        "Risk Score:",
        f"{score}/100" if score is not None else "Unknown"
    )

    findings = result.get(
        "risk_reasons",
        result.get("findings", [])
    )

    if findings:
        print("Security Findings:")

        for finding in findings:
            print(" -", finding)

    if "scanned_at" in result:
        print("Scanned At:", result["scanned_at"])

    if "event_type" in result:
        print("File Event:", result["event_type"])


def perform_scan():
    path = input("Enter file or directory path: ")
    path = Path(path.strip().strip('"'))

    if path.is_file():
        display_result(scan_file(path))

    elif path.is_dir():
        results = scan_directory(path)

        for result in results:
            display_result(result)

        print("\nTotal Files Scanned:", len(results))

    else:
        print("Invalid path!")


def display_history(threats_only=False):
    if threats_only:
        records = get_threat_history()
    else:
        records = get_scan_history()

    if not records:
        print("No records found.")
        return

    for record in records:
        display_result(record)


def display_statistics():
    stats = get_statistics()

    print("\n" + "=" * 50)
    print("EXTENSIONMASK - SECURITY STATISTICS")
    print("=" * 50)

    print("Total Scans:", stats["total_scans"])
    print("No Identified Risk:", stats["no_risk"])
    print("Flagged Scans:", stats["suspicious"])
    print("Low Risk:", stats["low"])
    print("Medium Risk:", stats["medium"])
    print("High Risk:", stats["high"])
    print("Critical Risk:", stats["critical"])
    print("Unknown:", stats["unknown"])


def start_monitoring():
    directory = input(
        "Enter directory to monitor: "
    ).strip().strip('"')

    if not directory:
        print("Please enter a directory path.")
        return

    monitor = DirectoryMonitor()

    try:
        monitor.start(directory)

        print("\n" + "=" * 50)
        print("EXTENSIONMASK - LIVE MONITOR")
        print("=" * 50)

        print("Monitoring:", monitor.directory)
        print("Status: ACTIVE")
        print("Press Ctrl+C to stop monitoring.")
        print("\nWaiting for file activity...\n")

        while monitor.is_running():

            for result in monitor.get_events():

                if "message" in result:
                    print(
                        "[ERROR]",
                        result["filename"],
                        result["message"]
                    )
                    continue

                if (result["risk_score"] or 0) > 0:
                    print("\n[SECURITY ALERT]")
                else:
                    print("\n[FILE ACTIVITY DETECTED]")

                display_result(result)

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nStopping directory monitoring...")

    finally:
        monitor.stop()
        print("Monitoring stopped.")


def main():
    initialize_database()

    while True:
        print("\n" + "=" * 50)
        print("EXTENSIONMASK - File Security Scanner")
        print("=" * 50)

        print("1. Scan File or Directory")
        print("2. View Scan History")
        print("3. View Threat History")
        print("4. View Security Statistics")
        print("5. Start Real-Time Monitoring")
        print("6. Exit")

        choice = input("\nSelect an option: ")

        try:
            if choice == "1":
                perform_scan()

            elif choice == "2":
                display_history()

            elif choice == "3":
                display_history(threats_only=True)

            elif choice == "4":
                display_statistics()

            elif choice == "5":
                start_monitoring()

            elif choice == "6":
                print("Exiting ExtensionMask...")
                break

            else:
                print("Invalid option!")

        except (OSError, ValueError, RuntimeError) as error:
            print("Operation failed:", error)


if __name__ == "__main__":
    main()
