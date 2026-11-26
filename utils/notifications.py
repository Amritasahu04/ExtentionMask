import logging
import time
import threading

from pathlib import Path
from queue import Queue, Full
from plyer import notification
from config import load_settings

logger = logging.getLogger(__name__)

SEVERITY_LEVELS = {
    "None": 0,
    "Unknown": 0,
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4
}


class NotificationManager:

    def __init__(
        self,
        enabled=True,
        minimum_severity="Medium",
        cooldown=30
    ):

        self.enabled = enabled
        self.minimum_severity = minimum_severity
        self.cooldown = cooldown

        self.recent_alerts = {}
        self.lock = threading.Lock()

        self.queue = Queue(maxsize=50)

        self.worker = threading.Thread(
            target=self.process_notifications,
            daemon=True
        )

        self.worker.start()

    def configure(
        self,
        enabled=True,
        minimum_severity="Medium",
        cooldown=30
    ):

        if minimum_severity not in SEVERITY_LEVELS:
            raise ValueError("Invalid severity level")

        with self.lock:

            self.enabled = bool(enabled)
            self.minimum_severity = minimum_severity
            self.cooldown = max(0, int(cooldown))

    def should_notify(self, result):

        if not self.enabled:
            return False

        if result.get("status") == "Error":
            return False

        severity = result.get("severity", "Unknown")

        current_level = SEVERITY_LEVELS.get(
            severity, 0
        )

        required_level = SEVERITY_LEVELS.get(
            self.minimum_severity, 2
        )

        if current_level == 0:
            return False

        return current_level >= required_level

    def notify_threat(self, result):

        with self.lock:

            if not self.should_notify(result):
                return False

            file_path = result.get(
                "path",
                result.get("file_path", "")
            )

            severity = result.get(
                "severity", "Unknown"
            )

            key = (str(file_path), severity)

            current_time = time.monotonic()

            self.recent_alerts = {
                item: timestamp
                for item, timestamp
                in self.recent_alerts.items()
                if current_time - timestamp
                < self.cooldown
            }

            if key in self.recent_alerts:
                return False

            filename = result.get(
                "filename",
                Path(file_path).name
            )

            score = result.get("risk_score", 0)

            findings = (
                result.get("risk_reasons")
                or result.get("threats")
                or ["Suspicious file activity"]
            )

            if isinstance(findings, str):
                finding = findings
            else:
                finding = findings[0]

            message = (
                f"File: {filename}\n"
                f"Severity: {severity}\n"
                f"Risk: {score}/100\n"
                f"{finding}"
            )

            try:

                self.queue.put_nowait((
                    "Suspicious File Detected",
                    message
                ))

            except Full:

                logger.warning(
                    "Notification queue is full"
                )

                return False

            self.recent_alerts[key] = current_time

            return True

    def process_notifications(self):

        while True:

            title, message = self.queue.get()

            try:

                notification.notify(
                    title=title,
                    message=message[:240],
                    app_name="ExtensionMask",
                    timeout=8
                )

                logger.info(
                     "Desktop security notification submitted"
                )

            except Exception as error:

                logger.error(
                    "Notification failed: %s",
                    error
                )

            finally:

                self.queue.task_done()


notification_manager = NotificationManager()
def apply_notification_settings():

    settings = load_settings()

    notification_manager.configure(
        enabled=settings["notifications_enabled"],
        minimum_severity=settings[
            "notification_min_severity"
        ],
        cooldown=settings[
            "notification_cooldown"
        ]
    )

    logger.info(
        "Notification preferences applied"
    )


apply_notification_settings()