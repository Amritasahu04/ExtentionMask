import hashlib
import shutil
import uuid

from pathlib import Path
from threading import RLock

from config import (
    BASE_DIR,
    DATA_DIR,
    QUARANTINE_DIR,
    initialize_directories
)

from core.scanner import scan_file

from database.db import (
    initialize_quarantine_table,
    save_quarantine_record,
    get_quarantine_record,
    get_quarantine_history,
    update_quarantine_status
)


operation_lock = RLock()


# Generate SHA-256 fingerprint
def calculate_sha256(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            chunk = file.read(65536)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


# Validate the stored quarantine path
def validate_quarantine_path(file_path):

    path = Path(file_path)

    if path.is_symlink():
        raise ValueError(
            "Symbolic links are not allowed"
        )

    path = path.resolve()

    if path.parent != QUARANTINE_DIR.resolve():
        raise ValueError(
            "Invalid quarantine file location"
        )

    if path.suffix != ".quarantine":
        raise ValueError(
            "Invalid quarantine file extension"
        )

    return path


# Validate an original file location
def validate_original_path(file_path):

    path = Path(file_path)

    if path.is_symlink():
        raise ValueError(
            "Symbolic links are not allowed"
        )

    path = path.resolve()

    if path.is_relative_to(DATA_DIR.resolve()):
        raise ValueError(
            "Cannot quarantine internal application data"
        )

    if path.is_relative_to(BASE_DIR.resolve()):

        test_directory = BASE_DIR / "test_samples"

        if not path.is_relative_to(
            test_directory.resolve()
        ):
            raise ValueError(
                "Cannot quarantine application files"
            )

    return path


# Quarantine a suspicious file
def quarantine_file(file_path):

    with operation_lock:

        initialize_directories()
        initialize_quarantine_table()

        source = validate_original_path(file_path)

        if not source.is_file():
            raise FileNotFoundError(
                "The selected file does not exist"
            )

        # Re-scan the current file
        result = scan_file(
            source,
            source="Manual"
        )

        if result["status"] == "Error":
            raise ValueError(
                "Unable to analyze the selected file"
            )

        if (result["risk_score"] or 0) <= 0:
            raise ValueError(
                "No risk indicators detected. "
                "Quarantine is not required."
            )

        original_hash = calculate_sha256(source)

        unique_name = (
            uuid.uuid4().hex + ".quarantine"
        )

        destination = (
            QUARANTINE_DIR / unique_name
        )

        record = {
            "scan_id": result.get("scan_id"),
            "filename": source.name,
            "original_path": str(source),
            "quarantine_path": str(destination),
            "sha256": original_hash,
            "file_size": source.stat().st_size,
            "risk_score": result["risk_score"],
            "severity": result["severity"]
        }

        # Record the operation before moving the file
        record_id = save_quarantine_record(record)

        try:

            shutil.move(
                str(source),
                str(destination)
            )

            # Verify file integrity after moving
            new_hash = calculate_sha256(destination)

            if new_hash != original_hash:
                raise ValueError(
                    "File integrity verification failed"
                )

            update_quarantine_status(
                record_id,
                "Quarantined"
            )

        except Exception:

            # Attempt rollback without overwriting files
            if destination.is_file() and not source.exists():

                try:
                    shutil.move(
                        str(destination),
                        str(source)
                    )

                except OSError:
                    pass

            update_quarantine_status(
                record_id,
                "Failed"
            )

            raise

        return get_quarantine_record(record_id)


# Restore a quarantined file
def restore_file(record_id):

    with operation_lock:

        record = get_quarantine_record(record_id)

        if record is None:
            raise ValueError(
                "Quarantine record not found"
            )

        if record["status"] != "Quarantined":
            raise ValueError(
                "This file is not currently quarantined"
            )

        source = validate_quarantine_path(
            record["quarantine_path"]
        )

        destination = validate_original_path(
            record["original_path"]
        )

        if not source.is_file():
            raise FileNotFoundError(
                "Quarantined file is missing"
            )

        if destination.exists():
            raise FileExistsError(
                "A file already exists at the "
                "original location. Restoration cancelled."
            )

        if calculate_sha256(source) != record["sha256"]:
            raise ValueError(
                "File integrity verification failed. "
                "Restoration cancelled."
            )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        update_quarantine_status(
            record_id,
            "Restoring"
        )

        try:

            # Exclusive creation prevents overwriting
            with open(source, "rb") as input_file:

                with open(destination, "xb") as output_file:

                    shutil.copyfileobj(
                        input_file,
                        output_file
                    )

            if calculate_sha256(destination) != record["sha256"]:

                raise ValueError(
                    "Restored file integrity check failed"
                )

            source.unlink()

        except Exception:

            update_quarantine_status(
                record_id,
                "Failed"
            )

            raise

        update_quarantine_status(
            record_id,
            "Restored"
        )

        return str(destination)


# Permanently delete a quarantined file
def delete_quarantined_file(record_id):

    with operation_lock:

        record = get_quarantine_record(record_id)

        if record is None:
            raise ValueError(
                "Quarantine record not found"
            )

        if record["status"] != "Quarantined":
            raise ValueError(
                "This file is not currently quarantined"
            )

        path = validate_quarantine_path(
            record["quarantine_path"]
        )

        if not path.is_file():
            raise FileNotFoundError(
                "Quarantined file is missing"
            )

        update_quarantine_status(
            record_id,
            "Deleting"
        )

        try:

            path.unlink()

        except OSError:

            update_quarantine_status(
                record_id,
                "Quarantined"
            )

            raise

        update_quarantine_status(
            record_id,
            "Deleted"
        )

        return True


# Verify quarantined file integrity
def verify_integrity(record_id):

    record = get_quarantine_record(record_id)

    if record is None:
        raise ValueError(
            "Quarantine record not found"
        )

    if record["status"] != "Quarantined":
        return False

    path = validate_quarantine_path(
        record["quarantine_path"]
    )

    if not path.is_file():
        return False

    current_hash = calculate_sha256(path)

    return current_hash == record["sha256"]


# Retrieve active quarantined files
def get_quarantined_files():

    return get_quarantine_history(
        active_only=True
    )


# Retrieve quarantine statistics
def get_quarantine_statistics():

    records = get_quarantine_history()

    return {
        "total": len(records),

        "quarantined": sum(
            record["status"] == "Quarantined"
            for record in records
        ),

        "restored": sum(
            record["status"] == "Restored"
            for record in records
        ),

        "deleted": sum(
            record["status"] == "Deleted"
            for record in records
        ),

        "needs_review": sum(
            record["status"] in {
                "Pending",
                "Restoring",
                "Deleting",
                "Failed"
            }
            for record in records
        ),

        "storage_used": sum(
            record["file_size"]
            for record in records
            if record["status"] == "Quarantined"
        )
    }
