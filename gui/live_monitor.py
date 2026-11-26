import customtkinter as ctk

from datetime import datetime
from tkinter import filedialog, messagebox

from core.monitor import DirectoryMonitor
from gui.theme import *

import time

from config import (
    load_settings,
    MONITOR_DURATIONS
)

class LiveMonitor(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=BG_COLOR,
            corner_radius=0
        )

        self.monitor = DirectoryMonitor()

        self.selected_directory = ctk.StringVar()

        self.total_events = 0
        self.flagged_events = 0
        self.poll_id = None

        self.monitor_deadline = None

        self.build_ui()

    def build_ui(self):

        # Page heading
        ctk.CTkLabel(
            self,
            text="Live Monitor",
            font=FONT_TITLE,
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", pady=(5, 5))

        ctk.CTkLabel(
            self,
            text="Real-time file activity and security analysis.",
            font=FONT_SUBTITLE,
            text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 20))

        # Monitoring controls
        controls = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=12
        )
        controls.pack(fill="x", pady=(0, 15))

        header = ctk.CTkFrame(
            controls,
            fg_color="transparent"
        )
        header.pack(
            fill="x", padx=15, pady=15
        )

        ctk.CTkLabel(
            header,
            text="Monitoring Directory",
            font=FONT_HEADING
        ).pack(side="left")

        self.status_label = ctk.CTkLabel(
            header,
            text="INACTIVE",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY
        )
        self.status_label.pack(side="right")

        self.path_entry = ctk.CTkEntry(
            controls,
            textvariable=self.selected_directory,
            placeholder_text="Select a directory",
            fg_color=BG_COLOR,
            border_color=BORDER_COLOR,
            height=40
        )
        self.path_entry.pack(
            fill="x", padx=15, pady=(0, 15)
        )

        buttons = ctk.CTkFrame(
            controls,
            fg_color="transparent"
        )
        buttons.pack(
            fill="x", padx=15, pady=(0, 15)
        )

        self.browse_button = ctk.CTkButton(
            buttons,
            text="Browse",
            command=self.select_directory
        )
        self.browse_button.pack(
            side="left", padx=(0, 10)
        )

        self.start_button = ctk.CTkButton(
            buttons,
            text="Start Monitoring",
            fg_color="#15803D",
            hover_color="#166534",
            command=self.start_monitoring
        )
        self.start_button.pack(
            side="left", padx=5
        )

        self.stop_button = ctk.CTkButton(
            buttons,
            text="Stop Monitoring",
            fg_color="#DC2626",
            hover_color="#B91C1C",
            state="disabled",
            command=self.stop_monitoring
        )
        self.stop_button.pack(side="right")

        # Monitoring statistics
        stats = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        stats.pack(fill="x", pady=(0, 15))

        self.total_label = self.create_stat(
            stats,
            "Files Analyzed",
            PRIMARY_COLOR
        )

        self.flagged_label = self.create_stat(
            stats,
            "Flagged Events",
            DANGER_COLOR
        )

        # Activity feed
        feed_header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        feed_header.pack(
            fill="x", pady=(0, 10)
        )

        ctk.CTkLabel(
            feed_header,
            text="Live Activity Feed",
            font=FONT_HEADING
        ).pack(side="left")

        ctk.CTkButton(
            feed_header,
            text="Clear Feed",
            width=100,
            fg_color=BORDER_COLOR,
            command=self.clear_feed
        ).pack(side="right")

        self.activity_feed = ctk.CTkScrollableFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=12
        )
        self.activity_feed.pack(
            fill="both", expand=True
        )

        self.add_message(
            "Select a directory to begin monitoring.",
            TEXT_SECONDARY
        )

    def create_stat(self, parent, title, color):

        card = ctk.CTkFrame(
            parent,
            fg_color=CARD_COLOR,
            corner_radius=10
        )
        card.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        ).pack(pady=(10, 0))

        value = ctk.CTkLabel(
            card,
            text="0",
            font=FONT_STAT,
            text_color=color
        )
        value.pack(pady=(0, 10))

        return value

    def select_directory(self):

        directory = filedialog.askdirectory()

        if directory:
            self.selected_directory.set(directory)

    def start_monitoring(self):

        if self.monitor.is_running():
            return

        directory = (
            self.selected_directory.get().strip()
        )

        if not directory:

            messagebox.showwarning(
                "Directory Required",
                "Please select a directory."
            )
            return

        try:
            self.monitor.start(directory)

        except Exception as error:

            self.monitor.stop()

            messagebox.showerror(
                "Monitoring Error",
                str(error)
            )
            return

        self.status_label.configure(
            text="ACTIVE",
            text_color=SUCCESS_COLOR
        )

        self.start_button.configure(
            state="disabled"
        )

        self.stop_button.configure(
            state="normal"
        )

        self.browse_button.configure(
            state="disabled"
        )

        self.path_entry.configure(
            state="disabled"
        )

        settings = load_settings()

        duration_name = settings["monitor_duration"]

        duration = MONITOR_DURATIONS.get(
            duration_name
        )

        self.monitor_deadline = (
            time.monotonic() + duration
            if duration is not None
            else None
        )

        self.add_message(
            f"Monitoring started: {self.monitor.directory}",
            SUCCESS_COLOR
        )

        self.add_message(
            f"Monitoring duration: {duration_name}",
            TEXT_SECONDARY
        )

        self.poll_events()


        self.poll_events()

    def stop_monitoring(self):

        if self.poll_id is not None:
            self.after_cancel(self.poll_id)
            self.poll_id = None

        self.monitor.stop()
        self.monitor_deadline = None

        # Display completed events before stopping
        for result in self.monitor.get_events():
            self.handle_event(result)

        self.status_label.configure(
            text="INACTIVE",
            text_color=TEXT_SECONDARY
        )

        self.start_button.configure(
            state="normal"
        )

        self.stop_button.configure(
            state="disabled"
        )

        self.browse_button.configure(
            state="normal"
        )

        self.path_entry.configure(
            state="normal"
        )

        self.add_message(
            "Directory monitoring stopped.",
            TEXT_SECONDARY
        )

    def poll_events(self):

        self.poll_id = None

        for result in self.monitor.get_events():
            self.handle_event(result)

        if self.monitor_deadline is not None:

            remaining = (
                self.monitor_deadline
                - time.monotonic()
            )

            if remaining <= 0:

                self.add_message(
                    "Monitoring duration completed.",
                    WARNING_COLOR
                )

                self.stop_monitoring()
                return

            minutes, seconds = divmod(
                int(remaining), 60
            )

            self.status_label.configure(
                text=f"ACTIVE | {minutes:02d}:{seconds:02d}",
                text_color=SUCCESS_COLOR
            )

        if self.monitor.is_running():

            self.poll_id = self.after(
                500, self.poll_events
            )

        else:
            self.stop_monitoring()


    def handle_event(self, result):

        if "message" in result:

            self.add_message(
                f"Error: {result['filename']} - "
                f"{result['message']}",
                DANGER_COLOR
            )
            return

        self.total_events += 1

        if (result["risk_score"] or 0) > 0:
            self.flagged_events += 1

        self.total_label.configure(
            text=str(self.total_events)
        )

        self.flagged_label.configure(
            text=str(self.flagged_events)
        )

        self.add_event(result)

    def add_event(self, result):

        severity = result["severity"]

        color = SEVERITY_COLORS.get(
            severity, TEXT_SECONDARY
        )

        row = ctk.CTkFrame(
            self.activity_feed,
            fg_color=BG_COLOR,
            corner_radius=8
        )
        row.pack(
            fill="x", padx=5, pady=5
        )

        details = ctk.CTkFrame(
            row, fg_color="transparent"
        )
        details.pack(
            side="left",
            fill="x",
            expand=True,
            padx=12,
            pady=10
        )

        ctk.CTkLabel(
            details,
            text=result["filename"],
            font=FONT_BODY,
            text_color=TEXT_PRIMARY,
            wraplength=400,
            justify="left"
        ).pack(anchor="w")

        timestamp = datetime.now().strftime(
            "%H:%M:%S"
        )

        event_type = result.get(
            "event_type", "File Activity"
        )

        ctk.CTkLabel(
            details,
            text=f"{timestamp} | {event_type}",
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        ).pack(anchor="w")

        findings = ", ".join(
            result.get("risk_reasons", [])
        )

        if findings:

            ctk.CTkLabel(
                details,
                text=findings,
                font=FONT_SMALL,
                text_color=color,
                wraplength=400,
                justify="left"
            ).pack(anchor="w")

        score = result["risk_score"]
        score_text = (
            str(score) if score is not None else "?"
        )

        ctk.CTkLabel(
            row,
            text=f"{severity} | {score_text}/100",
            font=FONT_BODY,
            text_color=color
        ).pack(
            side="right", padx=12
        )

        self.limit_feed()

    def add_message(self, message, color):

        timestamp = datetime.now().strftime(
            "%H:%M:%S"
        )

        ctk.CTkLabel(
            self.activity_feed,
            text=f"[{timestamp}] {message}",
            font=FONT_SMALL,
            text_color=color,
            wraplength=600,
            justify="left"
        ).pack(
            anchor="w", padx=10, pady=8
        )

        self.limit_feed()

    def limit_feed(self):

        widgets = self.activity_feed.winfo_children()

        # Prevent unlimited widget accumulation
        if len(widgets) > 200:

            for widget in widgets[:-200]:
                widget.destroy()

    def clear_feed(self):

        for widget in self.activity_feed.winfo_children():
            widget.destroy()

    def destroy(self):

        if self.poll_id is not None:
            self.after_cancel(self.poll_id)
            self.poll_id = None

        self.monitor.stop()

        super().destroy()
