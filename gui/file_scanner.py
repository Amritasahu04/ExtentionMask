import customtkinter as ctk
import threading

from pathlib import Path
from queue import Queue, Empty
from tkinter import filedialog, ttk, messagebox

from core.scanner import scan_file, scan_directory
from gui.theme import *


class FileScanner(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=BG_COLOR,
            corner_radius=0
        )

        self.selected_path = ctk.StringVar()
        self.result_queue = Queue()
        self.scanning = False
        self.results = []
        self.poll_id = None

        self.build_ui()

    def build_ui(self):

        ctk.CTkLabel(
            self,
            text="File Scanner",
            font=FONT_TITLE,
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", pady=(5, 5))

        ctk.CTkLabel(
            self,
            text="Analyze files for potential identity spoofing.",
            font=FONT_SUBTITLE,
            text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 20))

        # File selection panel
        panel = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=12
        )
        panel.pack(fill="x", pady=(0, 15))

        self.path_entry = ctk.CTkEntry(
            panel,
            textvariable=self.selected_path,
            placeholder_text="Select a file or folder",
            height=40,
            fg_color=BG_COLOR,
            border_color=BORDER_COLOR
        )
        self.path_entry.pack(
            fill="x", padx=15, pady=15
        )

        buttons = ctk.CTkFrame(
            panel, fg_color="transparent"
        )
        buttons.pack(
            fill="x", padx=15, pady=(0, 15)
        )

        self.file_button = ctk.CTkButton(
            buttons,
            text="Select File",
            command=self.select_file
        )
        self.file_button.pack(
            side="left", padx=(0, 10)
        )

        self.folder_button = ctk.CTkButton(
            buttons,
            text="Select Folder",
            command=self.select_folder
        )
        self.folder_button.pack(side="left")

        self.scan_button = ctk.CTkButton(
            buttons,
            text="Start Scan",
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            command=self.start_scan
        )
        self.scan_button.pack(side="right")

        # Scan progress
        self.progress = ctk.CTkProgressBar(
            self,
            mode="indeterminate",
            progress_color=PRIMARY_COLOR
        )
        self.progress.pack(fill="x", pady=5)
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready to scan",
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        )
        self.status_label.pack(
            anchor="w", pady=(0, 10)
        )

        # Statistics cards
        stats = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        stats.pack(fill="x", pady=(0, 15))

        self.stat_labels = {}

        for name, color in [
            ("Scanned", PRIMARY_COLOR),
            ("Flagged", DANGER_COLOR),
            ("Unverified", TEXT_SECONDARY)
        ]:

            card = ctk.CTkFrame(
                stats,
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
                text=name,
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

            self.stat_labels[name] = value

        # Results table
        table_frame = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=12
        )
        table_frame.pack(
            fill="both", expand=True
        )

        ctk.CTkLabel(
            table_frame,
            text="Scan Results",
            font=FONT_HEADING
        ).pack(
            anchor="w", padx=15, pady=10
        )

        self.create_table(table_frame)

        ctk.CTkButton(
            table_frame,
            text="View File Details",
            command=self.show_details
        ).pack(
            anchor="e", padx=15, pady=10
        )

    def create_table(self, parent):

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Scanner.Treeview",
            background=CARD_COLOR,
            foreground=TEXT_PRIMARY,
            fieldbackground=CARD_COLOR,
            rowheight=32,
            borderwidth=0,
            font=FONT_BODY
        )

        style.configure(
            "Scanner.Treeview.Heading",
            background=BORDER_COLOR,
            foreground=TEXT_PRIMARY,
            font=(FONT_FAMILY, 12, "bold")
        )

        style.map(
            "Scanner.Treeview",
            background=[
                ("selected", PRIMARY_HOVER)
            ]
        )

        columns = (
            "filename",
            "declared",
            "actual",
            "score",
            "severity"
        )

        container = ctk.CTkFrame(
            parent, fg_color="transparent"
        )
        container.pack(
            fill="both", expand=True, padx=15
        )

        self.table = ttk.Treeview(
            container,
            columns=columns,
            show="headings",
            style="Scanner.Treeview"
        )

        headings = [
            ("filename", "Filename", 220),
            ("declared", "Declared", 90),
            ("actual", "Detected", 90),
            ("score", "Risk Score", 90),
            ("severity", "Severity", 90)
        ]

        for column, title, width in headings:
            self.table.heading(
                column, text=title
            )
            self.table.column(
                column,
                width=width,
                minwidth=60,
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
            container,
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
            expand=True
        )

        self.table.bind(
            "<Double-1>",
            lambda event: self.show_details()
        )

    def select_file(self):

        path = filedialog.askopenfilename()

        if path:
            self.selected_path.set(path)

    def select_folder(self):

        path = filedialog.askdirectory()

        if path:
            self.selected_path.set(path)

    def start_scan(self):

        if self.scanning:
            return

        path = self.selected_path.get().strip()

        if not path or not Path(path).exists():
            messagebox.showwarning(
                "Invalid Path",
                "Please select a valid file or folder."
            )
            return

        self.scanning = True
        self.results = []

        for item in self.table.get_children():
            self.table.delete(item)

        for label in self.stat_labels.values():
            label.configure(text="0")

        self.scan_button.configure(
            state="disabled"
        )
        self.file_button.configure(
            state="disabled"
        )
        self.folder_button.configure(
            state="disabled"
        )
        self.path_entry.configure(
            state="disabled"
        )

        self.status_label.configure(
            text="Scanning...",
            text_color=PRIMARY_COLOR
        )

        self.progress.start()

        threading.Thread(
            target=self.scan_worker,
            args=(path,),
            daemon=True
        ).start()

        self.check_results()

    def scan_worker(self, path):

        try:
            if Path(path).is_file():
                results = [scan_file(path)]

            elif Path(path).is_dir():
                results = scan_directory(path)

            else:
                raise ValueError("Invalid path")

            self.result_queue.put(
                ("success", results)
            )

        except Exception as error:
            self.result_queue.put(
                ("error", str(error))
            )

    def check_results(self):

        self.poll_id = None

        try:
            status, data = (
                self.result_queue.get_nowait()
            )

        except Empty:
            self.poll_id = self.after(
                100, self.check_results
            )
            return

        self.scanning = False

        self.progress.stop()
        self.progress.set(0)

        self.scan_button.configure(
            state="normal"
        )
        self.file_button.configure(
            state="normal"
        )
        self.folder_button.configure(
            state="normal"
        )
        self.path_entry.configure(
            state="normal"
        )

        if status == "error":

            self.status_label.configure(
                text="Scan failed",
                text_color=DANGER_COLOR
            )

            messagebox.showerror(
                "Scan Error", data
            )
            return

        self.results = data
        self.display_results()

        self.status_label.configure(
            text=f"Scan completed: {len(data)} files",
            text_color=SUCCESS_COLOR
        )

    def display_results(self):

        flagged = 0
        unverified = 0

        for index, result in enumerate(self.results):

            score = result["risk_score"]
            severity = result["severity"]

            if (score or 0) > 0:
                flagged += 1

            if severity == "Unknown":
                unverified += 1

            self.table.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    result["filename"],
                    result["declared_extension"] or "-",
                    result["actual_type"],
                    score if score is not None else "-",
                    severity
                ),
                tags=(severity,)
            )

        self.stat_labels["Scanned"].configure(
            text=str(len(self.results))
        )

        self.stat_labels["Flagged"].configure(
            text=str(flagged)
        )

        self.stat_labels["Unverified"].configure(
            text=str(unverified)
        )

    def show_details(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showinfo(
                "File Details",
                "Please select a file from the table."
            )
            return

        result = self.results[int(selected[0])]

        findings = "\n".join(
            result.get("risk_reasons", [])
        ) or "No risk indicators detected."

        details = (
            f"Filename: {result['filename']}\n\n"
            f"Path: {result['path']}\n\n"
            f"Declared: {result['declared_extension']}\n"
            f"Detected: {result['actual_type']}\n"
            f"Status: {result['status']}\n"
            f"Risk Score: {result['risk_score']}\n"
            f"Severity: {result['severity']}\n\n"
            f"Security Findings:\n{findings}"
        )

        messagebox.showinfo(
            "File Analysis Details", details
        )

    def destroy(self):

        if self.poll_id is not None:
            self.after_cancel(self.poll_id)
            self.poll_id = None

        super().destroy()
