import customtkinter as ctk

from tkinter import messagebox

from config import (
    APP_NAME,
    APP_VERSION,
    DB_PATH,
    DEFAULT_SETTINGS,
    MONITOR_DURATIONS,
    load_settings,
    save_settings
)

from gui.theme import *


class Settings(ctk.CTkScrollableFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=BG_COLOR,
            corner_radius=0
        )

        settings = load_settings()

        self.duration_var = ctk.StringVar(
            value=settings["monitor_duration"]
        )

        self.delay_var = ctk.DoubleVar(
            value=settings["scan_delay"]
        )

        self.build_ui()

    def build_ui(self):

        ctk.CTkLabel(
            self,
            text="Settings",
            font=FONT_TITLE
        ).pack(anchor="w", pady=(5, 5))

        ctk.CTkLabel(
            self,
            text="Manage application preferences.",
            font=FONT_SUBTITLE,
            text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 20))

        # Monitoring preferences
        monitor_card = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=12
        )
        monitor_card.pack(
            fill="x", pady=(0, 20)
        )

        ctk.CTkLabel(
            monitor_card,
            text="Monitoring Preferences",
            font=FONT_HEADING
        ).pack(
            anchor="w", padx=20, pady=15
        )

        duration_row = ctk.CTkFrame(
            monitor_card,
            fg_color="transparent"
        )
        duration_row.pack(
            fill="x", padx=20, pady=10
        )

        details = ctk.CTkFrame(
            duration_row,
            fg_color="transparent"
        )
        details.pack(side="left")

        ctk.CTkLabel(
            details,
            text="Monitoring Duration",
            font=FONT_BODY
        ).pack(anchor="w")

        ctk.CTkLabel(
            details,
            text="Automatically stop monitoring "
                 "after a selected period.",
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        ).pack(anchor="w")

        ctk.CTkOptionMenu(
            duration_row,
            variable=self.duration_var,
            values=list(MONITOR_DURATIONS.keys()),
            width=150
        ).pack(side="right")

        # File activity delay
        delay_row = ctk.CTkFrame(
            monitor_card,
            fg_color="transparent"
        )
        delay_row.pack(
            fill="x", padx=20, pady=15
        )

        ctk.CTkLabel(
            delay_row,
            text="File Activity Delay",
            font=FONT_BODY
        ).pack(side="left")

        self.delay_label = ctk.CTkLabel(
            delay_row,
            text=f"{self.delay_var.get():.1f} seconds",
            font=FONT_BODY,
            text_color=PRIMARY_COLOR
        )
        self.delay_label.pack(side="right")

        ctk.CTkSlider(
            monitor_card,
            from_=1,
            to=10,
            number_of_steps=18,
            variable=self.delay_var,
            command=self.update_delay
        ).pack(
            fill="x", padx=20, pady=(0, 10)
        )

        ctk.CTkLabel(
            monitor_card,
            text="Wait for file activity to settle "
                 "before performing an automatic scan.",
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        ).pack(
            anchor="w", padx=20, pady=(0, 15)
        )

        ctk.CTkLabel(
            monitor_card,
            text="Changes apply to the next monitoring session.",
            font=FONT_SMALL,
            text_color=WARNING_COLOR
        ).pack(
            anchor="w", padx=20, pady=(0, 15)
        )

        # Application information
        about_card = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=12
        )
        about_card.pack(
            fill="x", pady=(0, 20)
        )

        ctk.CTkLabel(
            about_card,
            text="Application Information",
            font=FONT_HEADING
        ).pack(
            anchor="w", padx=20, pady=15
        )

        information = [
            ("Application", APP_NAME),
            ("Version", APP_VERSION),
            ("Project Type", "College Mini Project"),
            ("Domain", "Cybersecurity Analysis & Monitoring"),
            ("Language", "Python"),
            ("GUI Framework", "CustomTkinter"),
            ("Database", "SQLite"),
            ("Monitoring Engine", "Watchdog"),
            ("Detection Method", "File Signature Analysis"),
            ("Database Location", str(DB_PATH))
        ]

        for title, value in information:

            row = ctk.CTkFrame(
                about_card,
                fg_color="transparent"
            )
            row.pack(
                fill="x", padx=20, pady=6
            )

            ctk.CTkLabel(
                row,
                text=title,
                font=FONT_BODY,
                text_color=TEXT_SECONDARY
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=value,
                font=FONT_BODY,
                wraplength=450,
                justify="right"
            ).pack(side="right")

        # Action buttons
        buttons = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        buttons.pack(fill="x", pady=10)

        ctk.CTkButton(
            buttons,
            text="Save Settings",
            command=self.save_preferences
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            buttons,
            text="Restore Defaults",
            fg_color=BORDER_COLOR,
            command=self.restore_defaults
        ).pack(side="right", padx=5)

    def update_delay(self, value):

        self.delay_label.configure(
            text=f"{value:.1f} seconds"
        )

    def save_preferences(self):

        settings = load_settings()

        settings.update({
            "monitor_duration": self.duration_var.get(),
            "scan_delay": round(
                self.delay_var.get(), 1
            )
        })

        try:

            save_settings(settings)

            messagebox.showinfo(
                "Settings Saved",
                "Preferences saved successfully.\n\n"
                "Monitoring changes apply to the "
                "next monitoring session."
            )

        except OSError as error:

            messagebox.showerror(
                "Settings Error",
                str(error)
            )

    def restore_defaults(self):

        self.duration_var.set(
            DEFAULT_SETTINGS["monitor_duration"]
        )

        self.delay_var.set(
            DEFAULT_SETTINGS["scan_delay"]
        )

        self.update_delay(
            DEFAULT_SETTINGS["scan_delay"]
        )

        messagebox.showinfo(
            "Defaults Restored",
            "Default values restored.\n"
            "Click Save Settings to apply them."
        )
