import customtkinter as ctk
import threading

from queue import Queue, Empty
from tkinter import ttk, messagebox

from database.db import get_quarantine_history

from core.quarantine import (
    get_quarantine_statistics,
    restore_file,
    delete_quarantined_file,
    verify_integrity
)

from gui.theme import *


class QuarantineView(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=BG_COLOR,
            corner_radius=0
        )

        self.records = {}
        self.stat_labels = {}
        self.action_buttons = []

        self.busy = False
        self.result_queue = Queue()
        self.poll_id = None

        self.filter_var = ctk.StringVar(
            value="All Records"
        )

        self.build_ui()
        self.refresh_records()

    def build_ui(self):

        # Page header
        header = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        header.pack(fill="x", pady=(5, 5))

        ctk.CTkLabel(
            header,
            text="Quarantine",
            font=FONT_TITLE
        ).pack(side="left")

        ctk.CTkButton(
            header,
            height=BUTTON_HEIGHT,
            corner_radius=BUTTON_RADIUS,
            font=FONT_BUTTON,
            text="Refresh",
            width=100,
            command=self.refresh_records
        ).pack(side="right")

        ctk.CTkLabel(
            self,
            text="Manage isolated files and security actions.",
            font=FONT_SUBTITLE,
            text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 20))

        # Statistics cards
        stats = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        stats.pack(fill="x", pady=(0, 20))

        card_data = [
            ("Quarantined", HIGH_COLOR),
            ("Restored", SUCCESS_COLOR),
            ("Deleted", DANGER_COLOR),
            ("Storage Used", PRIMARY_COLOR)
        ]

        for title, color in card_data:

            card = ctk.CTkFrame(
                stats,
                fg_color=CARD_COLOR,
                corner_radius=CARD_RADIUS,
                border_width=1,
                border_color=BORDER_COLOR
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
            ).pack(pady=(12, 0))

            value = ctk.CTkLabel(
                card,
                text="0",
                font=FONT_STAT,
                text_color=color
            )
            value.pack(pady=(0, 12))

            self.stat_labels[title] = value

        # History header
        history_header = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        history_header.pack(
            fill="x", pady=(0, 10)
        )

        ctk.CTkLabel(
            history_header,
            text="Quarantine History",
            font=FONT_HEADING
        ).pack(side="left")

        ctk.CTkOptionMenu(
            history_header,
            variable=self.filter_var,
            values=[
                "All Records",
                "Quarantined",
                "Restored",
                "Deleted",
                "Needs Review"
            ],
            width=150,
            command=lambda value: self.refresh_records()
        ).pack(side="right")

        # Table container
        table_frame = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=CARD_RADIUS,
            border_width=1,
            border_color=BORDER_COLOR
        )
        table_frame.pack(
            fill="both", expand=True
        )

        self.create_table(table_frame)

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        )
        self.status_label.pack(
            anchor="w", pady=8
        )

        # Action buttons
        actions = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        actions.pack(fill="x", pady=5)

        buttons = [
            (
                "View Details",
                BORDER_COLOR,
                self.show_details
            ),
            (
                "Verify Integrity",
                PRIMARY_COLOR,
                self.verify_selected
            ),
            (
                "Restore File",
                "#15803D",
                self.restore_selected
            ),
            (
                "Delete Permanently",
                "#DC2626",
                self.delete_selected
            )
        ]

        for title, color, command in buttons:

            button = ctk.CTkButton(
                actions,
                height=BUTTON_HEIGHT,
                corner_radius=BUTTON_RADIUS,
                font=FONT_BUTTON,
                text=title,
                fg_color=color,
                command=command
            )
            button.pack(
                side="left",
                fill="x",
                expand=True,
                padx=4
            )

            self.action_buttons.append(button)

    def create_table(self, parent):

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Quarantine.Treeview",
            background=CARD_COLOR,
            foreground=TEXT_PRIMARY,
            fieldbackground=CARD_COLOR,
            rowheight=TABLE_ROW_HEIGHT,
            borderwidth=0,
            font=FONT_BODY
        )

        style.configure(
            "Quarantine.Treeview.Heading",
            background=BORDER_COLOR,
            foreground=TEXT_PRIMARY,
            font=(FONT_FAMILY, 11, "bold")
        )

        style.map(
            "Quarantine.Treeview",
            background=[
                ("selected", ACTIVE_NAV_COLOR)
            ],
            foreground=[("selected", TEXT_PRIMARY)]
        )

        columns = (
            "id",
            "filename",
            "severity",
            "size",
            "status"
        )

        self.table = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Quarantine.Treeview"
        )

        headings = [
            ("id", "ID", 45),
            ("filename", "Filename", 230),
            ("severity", "Severity", 90),
            ("size", "Size", 90),
            ("status", "Status", 120)
        ]

        for column, title, width in headings:

            self.table.heading(
                column, text=title
            )

            self.table.column(
                column,
                width=width,
                minwidth=40,
                anchor="center"
            )

        self.table.column(
            "filename", anchor="w"
        )

        self.table.tag_configure(
            "Quarantined",
            foreground=HIGH_COLOR
        )

        self.table.tag_configure(
            "Restored",
            foreground=SUCCESS_COLOR
        )

        self.table.tag_configure(
            "Deleted",
            foreground=TEXT_SECONDARY
        )

        self.table.tag_configure(
            "Review",
            foreground=DANGER_COLOR
        )

        scrollbar = ttk.Scrollbar(
            parent,
            orient="vertical",
            command=self.table.yview
        )

        self.table.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right", fill="y"
        )

        self.table.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.table.bind(
            "<Double-1>",
            lambda event: self.show_details()
        )

    @staticmethod
    def format_size(size):

        size = float(size)

        for unit in ["B", "KB", "MB", "GB", "TB"]:

            if size < 1024 or unit == "TB":
                return f"{size:.1f} {unit}"

            size /= 1024

    def refresh_records(self):

        if self.busy:
            return

        stats = get_quarantine_statistics()

        self.stat_labels["Quarantined"].configure(
            text=str(stats["quarantined"])
        )

        self.stat_labels["Restored"].configure(
            text=str(stats["restored"])
        )

        self.stat_labels["Deleted"].configure(
            text=str(stats["deleted"])
        )

        self.stat_labels["Storage Used"].configure(
            text=self.format_size(
                stats["storage_used"]
            )
        )

        records = get_quarantine_history()

        selected_filter = self.filter_var.get()

        review_statuses = {
            "Pending",
            "Restoring",
            "Deleting",
            "Failed"
        }

        if selected_filter == "Needs Review":

            records = [
                record for record in records
                if record["status"] in review_statuses
            ]

        elif selected_filter != "All Records":

            records = [
                record for record in records
                if record["status"] == selected_filter
            ]

        self.records = {
            str(record["id"]): record
            for record in records
        }

        for item in self.table.get_children():
            self.table.delete(item)

        for record in records:

            status = record["status"]

            tag = (
                "Review"
                if status in review_statuses
                else status
            )

            self.table.insert(
                "",
                "end",
                iid=str(record["id"]),
                values=(
                    record["id"],
                    record["filename"],
                    record["severity"],
                    self.format_size(
                        record["file_size"]
                    ),
                    status
                ),
                tags=(tag,)
            )

        self.status_label.configure(
            text=(
                (f"{len(records)} records shown | " if records else "No matching quarantine records | ") + 
                f"{stats['needs_review']} need review"
            ),
            text_color=TEXT_SECONDARY
        )

    def get_selected_record(
        self, active_only=False
    ):

        selected = self.table.selection()

        if not selected:

            messagebox.showinfo(
                "Selection Required",
                "Please select a quarantine record."
            )
            return None

        record = self.records.get(selected[0])

        if record is None:
            return None

        if active_only and (
            record["status"] != "Quarantined"
        ):

            messagebox.showwarning(
                "Invalid Operation",
                "This file is not currently quarantined."
            )
            return None

        return record

    def show_details(self):

        record = self.get_selected_record()

        if record is None:
            return

        details = (
            f"Record ID: {record['id']}\n\n"
            f"Filename: {record['filename']}\n\n"
            f"Original Path:\n"
            f"{record['original_path']}\n\n"
            f"Quarantine Path:\n"
            f"{record['quarantine_path']}\n\n"
            f"SHA-256:\n{record['sha256']}\n\n"
            f"Size: "
            f"{self.format_size(record['file_size'])}\n"
            f"Risk Score: {record['risk_score']}/100\n"
            f"Severity: {record['severity']}\n"
            f"Status: {record['status']}\n\n"
            f"Quarantined At:\n"
            f"{record['quarantined_at']}"
        )

        messagebox.showinfo(
            "Quarantine Record Details",
            details
        )

    def verify_selected(self):

        record = self.get_selected_record(
            active_only=True
        )

        if record is None:
            return

        self.run_operation(
            "verify",
            verify_integrity,
            record["id"]
        )

    def restore_selected(self):

        record = self.get_selected_record(
            active_only=True
        )

        if record is None:
            return

        confirmed = messagebox.askyesno(
            "Restore File",
            f"Restore '{record['filename']}' "
            "to its original location?\n\n"
            "The file may still contain security risks."
        )

        if not confirmed:
            return

        self.run_operation(
            "restore",
            restore_file,
            record["id"]
        )

    def delete_selected(self):

        record = self.get_selected_record(
            active_only=True
        )

        if record is None:
            return

        confirmed = messagebox.askyesno(
            "Permanent Deletion",
            f"Permanently delete "
            f"'{record['filename']}'?\n\n"
            "This action cannot be undone "
            "through ExtensionMask.",
            icon="warning"
        )

        if not confirmed:
            return

        self.run_operation(
            "delete",
            delete_quarantined_file,
            record["id"]
        )

    def run_operation(
        self, action, function, record_id
    ):

        if self.busy:
            return

        self.busy = True

        for button in self.action_buttons:
            button.configure(state="disabled")

        self.status_label.configure(
            text="Processing file operation...",
            text_color=PRIMARY_COLOR
        )

        threading.Thread(
            target=self.operation_worker,
            args=(action, function, record_id),
            daemon=True
        ).start()

        self.check_operation()

    def operation_worker(
        self, action, function, record_id
    ):

        try:

            result = function(record_id)

            self.result_queue.put(
                ("success", action, result)
            )

        except Exception as error:

            self.result_queue.put(
                ("error", action, str(error))
            )

    def check_operation(self):

        self.poll_id = None

        try:

            status, action, result = (
                self.result_queue.get_nowait()
            )

        except Empty:

            self.poll_id = self.after(
                100, self.check_operation
            )
            return

        self.busy = False

        for button in self.action_buttons:
            button.configure(state="normal")

        self.refresh_records()

        if status == "error":

            messagebox.showerror(
                "Operation Failed",
                result
            )
            return

        if action == "verify":

            if result:

                messagebox.showinfo(
                    "Integrity Verified",
                    "SHA-256 hash matches.\n\n"
                    "The file has not changed "
                    "since quarantine."
                )

            else:

                messagebox.showwarning(
                    "Integrity Warning",
                    "The file is missing or its "
                    "SHA-256 hash does not match."
                )

        elif action == "restore":

            messagebox.showinfo(
                "File Restored",
                f"File restored successfully:\n\n"
                f"{result}"
            )

        elif action == "delete":

            messagebox.showinfo(
                "File Deleted",
                "The quarantined file has been deleted."
            )

    def destroy(self):

        if self.poll_id is not None:

            self.after_cancel(self.poll_id)
            self.poll_id = None

        super().destroy()
