import time
import logging

from pathlib import Path
from threading import Lock, Thread, Event
from queue import Queue, Empty

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from core.scanner import scan_file
from config import DATA_DIR, load_settings


class FileMonitorHandler(FileSystemEventHandler):

    def __init__(self, event_queue):
        super().__init__()

        self.event_queue = event_queue
        self.pending_files = {}
        self.lock = Lock()
        self.scan_delay = load_settings()["scan_delay"]

        self.ignored_extensions = {
            ".tmp", ".part", ".crdownload"
        }

    def schedule_scan(self, file_path, event_type):

        try:
            path = Path(file_path)

            if path.is_symlink():
                return

            path = path.resolve()

            if path.is_relative_to(DATA_DIR.resolve()):
                return

            if path.suffix.lower() in self.ignored_extensions:
                return

            with self.lock:
                self.pending_files[str(path)] = (
                    time.monotonic(),
                    event_type
                )

        except (OSError, RuntimeError):
            logging.exception(
                "Unable to schedule file scan"
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

            with self.lock:
                self.pending_files.pop(
                    str(Path(event.src_path).absolute()),
                    None
                )

            self.schedule_scan(
                event.dest_path, "Renamed/Moved"
            )

    def process_pending(self, stop_event):

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

            if stop_event.is_set():
                break

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
        self.worker = None

        self.event_queue = Queue()
        self.stop_event = Event()

        self.directory = None

    def start(self, directory_path):

        directory = Path(directory_path).resolve()

        if not directory.is_dir():
            raise ValueError("Invalid directory path")

        if directory.is_relative_to(DATA_DIR.resolve()):
            raise ValueError(
                "Cannot monitor internal application data"
            )

        if self.is_running():
            raise RuntimeError(
                "Monitoring is already active"
            )

        self.directory = str(directory)

        self.stop_event.clear()
        self.event_queue = Queue()

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

        self.worker = Thread(
            target=self.worker_loop,
            daemon=True
        )
        self.worker.start()

    def worker_loop(self):

        while not self.stop_event.is_set():

            self.handler.process_pending(
                self.stop_event
            )

            self.stop_event.wait(0.5)

    def stop(self):

        self.stop_event.set()

        if self.observer is not None:

            self.observer.stop()

            if self.observer.is_alive():
                self.observer.join()

            self.observer = None

        if self.worker is not None:

            self.worker.join()
            self.worker = None

        self.handler = None

    def is_running(self):

        return (
            self.observer is not None
            and self.observer.is_alive()
        )

    def get_events(self):

        events = []

        while True:

            try:
                events.append(
                    self.event_queue.get_nowait()
                )

            except Empty:
                break

        return events
