import pytest

from PIL import Image

import config
import core.quarantine as quarantine
import database.db as db


@pytest.fixture
def isolated_environment(tmp_path, monkeypatch):

    data_dir = tmp_path / "data"
    quarantine_dir = data_dir / "quarantine"
    db_path = data_dir / "test.db"

    data_dir.mkdir()
    quarantine_dir.mkdir()

    monkeypatch.setattr(
        config, "DATA_DIR", data_dir
    )

    monkeypatch.setattr(
        config, "QUARANTINE_DIR", quarantine_dir
    )

    monkeypatch.setattr(
        quarantine, "DATA_DIR", data_dir
    )

    monkeypatch.setattr(
        quarantine, "QUARANTINE_DIR", quarantine_dir
    )

    monkeypatch.setattr(
        db, "DB_PATH", db_path
    )

    db.initialize_database()
    db.initialize_quarantine_table()

    return tmp_path


def create_suspicious_file(directory):

    image_path = directory / "sample.jpg"

    Image.new(
        "RGB",
        (20, 20),
        "blue"
    ).save(image_path, "JPEG")

    suspicious_path = directory / "sample.pdf"

    image_path.rename(suspicious_path)

    return suspicious_path


def test_quarantine_file(isolated_environment):

    path = create_suspicious_file(
        isolated_environment
    )

    record = quarantine.quarantine_file(path)

    assert not path.exists()

    assert record["status"] == "Quarantined"

    assert quarantine.verify_integrity(
        record["id"]
    )


def test_restore_file(isolated_environment):

    path = create_suspicious_file(
        isolated_environment
    )

    original_hash = quarantine.calculate_sha256(path)

    record = quarantine.quarantine_file(path)

    quarantine.restore_file(record["id"])

    assert path.exists()

    assert quarantine.calculate_sha256(
        path
    ) == original_hash

    updated = db.get_quarantine_record(
        record["id"]
    )

    assert updated["status"] == "Restored"


def test_delete_file(isolated_environment):

    path = create_suspicious_file(
        isolated_environment
    )

    record = quarantine.quarantine_file(path)

    quarantine.delete_quarantined_file(
        record["id"]
    )

    updated = db.get_quarantine_record(
        record["id"]
    )

    assert updated["status"] == "Deleted"

    assert not quarantine.get_quarantined_files()


def test_restore_overwrite_protection(
    isolated_environment
):

    path = create_suspicious_file(
        isolated_environment
    )

    record = quarantine.quarantine_file(path)

    path.write_text("Existing file")

    with pytest.raises(FileExistsError):

        quarantine.restore_file(record["id"])

    assert path.read_text() == "Existing file"


def test_integrity_verification(
    isolated_environment
):

    from pathlib import Path

    path = create_suspicious_file(
        isolated_environment
    )

    record = quarantine.quarantine_file(path)

    stored_file = Path(
        record["quarantine_path"]
    )

    stored_file.write_bytes(b"Modified content")

    assert not quarantine.verify_integrity(
        record["id"]
    )

    with pytest.raises(ValueError):

        quarantine.restore_file(record["id"])


def test_reject_normal_file(
    isolated_environment
):

    path = isolated_environment / "normal.jpg"

    Image.new(
        "RGB",
        (20, 20),
        "blue"
    ).save(path, "JPEG")

    with pytest.raises(ValueError):

        quarantine.quarantine_file(path)

    assert path.exists()
