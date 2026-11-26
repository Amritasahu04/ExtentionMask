import csv
import customtkinter as ctk

from datetime import datetime
from tkinter import ttk, filedialog, messagebox

from database.db import (
    search_threat_history,
    get_statistics
)
from pathlib import Path
from core.quarantine import quarantine_file
from gui.theme import *


class ThreatLogs(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=BG_COLOR,
            corner_radius=0
        )

        self.records = []

        self.search_var = ctk.StringVar()
        self.severity_var = ctk.StringVar(
            value="All Severities"
        )
        self.source_var = ctk.StringVar(
            value="All Sources"
        )

        self.build_ui()
        self.refresh_logs()

    def build_ui(self):

        header = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        header.pack(fill="x", pady=(5, 5))

        ctk.CTkLabel(
            header,
            text="Threat Logs",
            font=FONT_TITLE
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Export CSV",
            command=self.export_csv
        ).pack(side="right")

        ctk.CTkLabel(
            self,
            text="Review recorded security findings.",
            font=FONT_SUBTITLE,
            text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 20))

        # Statistics
        stats_frame = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        stats_frame.pack(fill="x", pady=(0, 15))

        self.stat_labels = {}

        for title, color in [
            ("Total Findings", PRIMARY_COLOR),
            ("High Risk", HIGH_COLOR),
            ("Critical", DANGER_COLOR)
        ]:

            card = ctk.CTkFrame(
                stats_frame,
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

            self.stat_labels[title] = value

        # Search and filters
        filters = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=10
        )
        filters.pack(fill="x", pady=(0, 15))

        search = ctk.CTkEntry(
            filters,
            textvariable=self.search_var,
            placeholder_text="Search incidents...",
            fg_color=BG_COLOR,
            height=35
        )
        search.pack(
            side="left",
            fill="x",
            expand=True,
            padx=10,
            pady=12
        )

        search.bind(
            "<Return>",
            lambda event: self.refresh_logs()
        )

        ctk.CTkOptionMenu(
            filters,
            variable=self.severity_var,
            values=[
                "All Severities",
                "Low",
                "Medium",
                "High",
                "Critical"
            ],
            width=130,
            command=lambda value: self.refresh_logs()
        ).pack(side="left", padx=5)

        ctk.CTkOptionMenu(
            filters,
            variable=self.source_var,
            values=[
                "All Sources",
                "Manual",
                "Automatic"
            ],
            width=120,
            command=lambda value: self.refresh_logs()
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            filters,
            text="Search",
            width=75,
            command=self.refresh_logs
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            filters,
            text="Reset",
            width=65,
            fg_color=BORDER_COLOR,
            command=self.reset_filters
        ).pack(side="left", padx=(5, 10))

        # Table container
        table_frame = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=12
        )
        table_frame.pack(
            fill="both", expand=True
        )

        self.create_table(table_frame)

        footer = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        footer.pack(fill="x", pady=10)

        self.count_label = ctk.CTkLabel(
            footer,
            text="0 records",
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        )
        self.count_label.pack(side="left")

        ctk.CTkButton(
            footer,
            text="View Details",
            command=self.show_details
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            footer,
            text="Quarantine File",
            fg_color="#C2410C",
            hover_color="#9A3412",
            command=self.quarantine_selected
        ).pack(side="right", padx=5)


        ctk.CTkButton(
            footer,
            text="Refresh",
            width=90,
            fg_color=BORDER_COLOR,
            command=self.refresh_logs
        ).pack(side="right", padx=5)

    def create_table(self, parent):

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Threat.Treeview",
            background=CARD_COLOR,
            foreground=TEXT_PRIMARY,
            fieldbackground=CARD_COLOR,
            rowheight=34,
            borderwidth=0,
            font=FONT_BODY
        )

        style.configure(
            "Threat.Treeview.Heading",
            background=BORDER_COLOR,
            foreground=TEXT_PRIMARY,
            font=(FONT_FAMILY, 11, "bold")
        )

        style.map(
            "Threat.Treeview",
            background=[
                ("selected", PRIMARY_HOVER)
            ]
        )

        columns = (
            "id",
            "filename",
            "score",
            "severity",
            "source",
            "timestamp"
        )

        self.table = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            style="Threat.Treeview"
        )

        headings = [
            ("id", "ID", 45),
            ("filename", "Filename", 200),
            ("score", "Score", 60),
            ("severity", "Severity", 85),
            ("source", "Source", 85),
            ("timestamp", "Date & Time", 150)
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

        for severity, color in SEVERITY_COLORS.items():

            self.table.tag_configure(
                severity, foreground=color
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

    def refresh_logs(self):

        stats = get_statistics()

        self.stat_labels["Total Findings"].configure(
            text=str(stats["suspicious"])
        )

        self.stat_labels["High Risk"].configure(
            text=str(stats["high"])
        )

        self.stat_labels["Critical"].configure(
            text=str(stats["critical"])
        )

        self.records = search_threat_history(
            search=self.search_var.get(),
            severity=self.severity_var.get(),
            source=self.source_var.get(),
            limit=1000
        )

        for item in self.table.get_children():
            self.table.delete(item)

        for record in self.records:

            timestamp = record["scanned_at"]

            try:
                timestamp = datetime.fromisoformat(
                    timestamp
                ).strftime("%d-%m-%Y %H:%M:%S")

            except (ValueError, TypeError):
                pass

            self.table.insert(
                "",
                "end",
                iid=str(record["id"]),
                values=(
                    record["id"],
                    record["filename"],
                    record["risk_score"],
                    record["severity"],
                    record["scan_source"],
                    timestamp
                ),
                tags=(record["severity"],)
            )

        self.count_label.configure(
            text=f"{len(self.records)} records shown"
        )

    def reset_filters(self):

        self.search_var.set("")
        self.severity_var.set("All Severities")
        self.source_var.set("All Sources")

        self.refresh_logs()

    def show_details(self):

        selected = self.table.selection()

        if not selected:

            messagebox.showinfo(
                "Threat Details",
                "Please select a record."
            )
            return

        record = next(
            (
                item for item in self.records
                if str(item["id"]) == selected[0]
            ),
            None
        )

        if record is None:
            return

        findings = "\n".join(
            record.get("findings", [])
        )

        details = (
            f"Incident ID: {record['id']}\n\n"
            f"Filename: {record['filename']}\n"
            f"Path: {record['file_path']}\n\n"
            f"Declared Extension: "
            f"{record['declared_extension']}\n"
            f"Detected Type: {record['actual_type']}\n"
            f"Status: {record['status']}\n"
            f"Risk Score: {record['risk_score']}/100\n"
            f"Severity: {record['severity']}\n"
            f"Scan Source: {record['scan_source']}\n"
            f"Scanned At: {record['scanned_at']}\n\n"
            f"Security Findings:\n{findings}"
        )

        messagebox.showinfo(
            "Security Incident Details",
            details
        )
    def quarantine_selected(self):

        selected = self.table.selection()

        if not selected:

            messagebox.showinfo(
                "Selection Required",
                "Please select a threat record."
            )
            return

        record = next(
            (
                item for item in self.records
                if str(item["id"]) == selected[0]
            ),
            None
        )

        if record is None:
            return

        path = Path(record["file_path"])

        if not path.is_file():

            messagebox.showwarning(
                "File Unavailable",
                "The original file no longer exists "
                "at its recorded location.\n\n"
                "It may have been moved, deleted "
                "or quarantined."
            )
            return

        confirmed = messagebox.askyesno(
            "Quarantine File",
            f"Quarantine the current file at:\n\n"
            f"{path}\n\n"
            "The file will be re-scanned before "
            "being moved to quarantine.",
            icon="warning"
        )

        if not confirmed:
            return

        try:

            result = quarantine_file(path)

            self.refresh_logs()

            messagebox.showinfo(
                "Quarantine Successful",
                f"'{result['filename']}' has been "
                "successfully quarantined.\n\n"
                "Open the Quarantine page "
                "to manage the file."
            )

        except Exception as error:

            messagebox.showerror(
                "Quarantine Failed",
                str(error)
            )

    def export_csv(self):

        records = search_threat_history(
            search=self.search_var.get(),
            severity=self.severity_var.get(),
            source=self.source_var.get()
        )

        if not records:

            messagebox.showinfo(
                "Export Report",
                "No records available to export."
            )
            return

        filename = (
            "ExtensionMask_Report_"
            + datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".csv"
        )

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=filename,
            filetypes=[("CSV Files", "*.csv")]
        )

        if not path:
            return

        columns = [
            "id",
            "filename",
            "file_path",
            "declared_extension",
            "actual_type",
            "status",
            "risk_score",
            "severity",
            "findings",
            "scan_source",
            "scanned_at"
        ]

        try:

            with open(
                path,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=columns
                )

                writer.writeheader()

                for record in records:

                    row = {
                        key: record.get(key, "")
                        for key in columns
                    }

                    row["findings"] = "; ".join(
                        record.get("findings", [])
                    )

                    # Prevent spreadsheet formula injection
                    for key, value in row.items():

                        if isinstance(value, str):

                            if value.lstrip().startswith(
                                ("=", "+", "-", "@")
                            ) or value.startswith(
                                ("\t", "\r", "\n")
                            ):
                                row[key] = "'" + value

                    writer.writerow(row)

            messagebox.showinfo(
                "Export Successful",
                f"Exported {len(records)} records.\n\n"
                f"Saved to:\n{path}"
            )

        except OSError as error:

            messagebox.showerror(
                "Export Failed",
                str(error)
            )
