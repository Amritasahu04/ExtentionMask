import time
import logging

from pathlib import Path
from threading import Lock
from queue import Queue, Empty

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from core.scanner import scan_file
from config import DATA_DIR


class FileMonitorHandler(FileSystemEventHandler):

    def __init__(self, event_queue):
        super().__init__()

        self.event_queue = event_queue
        self.pending_files = {}
        self.lock = Lock()

        # Wait for file activity to settle
        self.scan_delay = 2.0

        self.ignored_extensions = {
            ".tmp", ".part", ".crdownload"
        }

    def schedule_scan(self, file_path, event_type):
        path = Path(file_path).resolve()

        # Ignore internal application data
        if path.is_relative_to(DATA_DIR.resolve()):
            return

        # Ignore incomplete downloads
        if path.suffix.lower() in self.ignored_extensions:
            return

        with self.lock:
            self.pending_files[str(path)] = (
                time.monotonic(),
                event_type
            )

    def on_created(self, event):
        if not event.is_directory:
            self.schedule_scan(
                event.src_path, "Created"
            )

    def on_modified(self, event):
        if not event.is_directory:
            self.schedule_scan(
                event.src_path, "Modified"
            )

    def on_moved(self, event):
        if not event.is_directory:
            self.schedule_scan(
                event.dest_path, "Renamed/Moved"
            )

    def process_pending(self):
        now = time.monotonic()
        ready = []

        with self.lock:
            for path, details in list(
                self.pending_files.items()
            ):
                timestamp, event_type = details

                if now - timestamp >= self.scan_delay:
                    ready.append((path, event_type))
                    del self.pending_files[path]

        for file_path, event_type in ready:
            path = Path(file_path)

            if not path.is_file() or path.is_symlink():
                continue

            try:
                result = scan_file(
                    file_path,
                    source="Automatic"
                )

                result["event_type"] = event_type

                self.event_queue.put(result)

            except Exception as error:
                logging.exception(
                    "Automatic scan failed"
                )

                self.event_queue.put({
                    "status": "Error",
                    "filename": path.name,
                    "message": str(error)
                })


class DirectoryMonitor:

    def __init__(self):
        self.observer = None
        self.handler = None
        self.event_queue = Queue()
        self.directory = None

    def start(self, directory_path):
        directory = Path(directory_path).resolve()

        if not directory.is_dir():
            raise ValueError("Invalid directory path")

        if self.is_running():
            raise RuntimeError(
                "Monitoring is already active"
            )

        self.directory = str(directory)

        self.handler = FileMonitorHandler(
            self.event_queue
        )

        self.observer = Observer()

        self.observer.schedule(
            self.handler,
            self.directory,
            recursive=True
        )

        self.observer.start()

    def stop(self):
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()

            self.observer = None
            self.handler = None

    def is_running(self):
        return (
            self.observer is not None
            and self.observer.is_alive()
        )

    def get_events(self):
        if self.handler is not None:
            self.handler.process_pending()

        events = []

        while True:
            try:
                events.append(
                    self.event_queue.get_nowait()
                )

            except Empty:
                break

        return events
