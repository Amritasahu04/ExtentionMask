from config import NOTIFICATION_SEVERITIES

from utils.notifications import (
    apply_notification_settings
)

from utils.logger import get_logger

logger = get_logger(__name__)
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
        notification_settings = load_settings()

        self.notification_enabled_var = ctk.BooleanVar(
            value=notification_settings[
                "notifications_enabled"
            ]
        )

        self.notification_severity_var = ctk.StringVar(
            value=notification_settings[
                "notification_min_severity"
            ]
        )

        self.notification_cooldown_var = ctk.DoubleVar(
            value=notification_settings[
                "notification_cooldown"
            ]
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
        self.build_notification_card()
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
    def build_notification_card(self):

        notification_card = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=12
        )

        notification_card.pack(
            fill="x",
            pady=(0, 20)
        )

        ctk.CTkLabel(
            notification_card,
            text="Notification Preferences",
            font=FONT_HEADING,
            text_color=TEXT_PRIMARY
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 15)
        )

        # Enable or disable notifications

        ctk.CTkSwitch(
            notification_card,
            text="Enable Desktop Notifications",
            variable=self.notification_enabled_var,
            onvalue=True,
            offvalue=False,
            font=FONT_BODY,
            progress_color=PRIMARY_COLOR
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 5)
        )

        ctk.CTkLabel(
            notification_card,
            text=(
                "Receive desktop alerts when "
                "suspicious files are detected."
            ),
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 20)
        )

        # Minimum alert severity

        ctk.CTkLabel(
            notification_card,
            text="Minimum Alert Severity",
            font=FONT_BODY,
            text_color=TEXT_PRIMARY
        ).pack(
            anchor="w",
            padx=20
        )

        ctk.CTkOptionMenu(
            notification_card,
            values=NOTIFICATION_SEVERITIES,
            variable=self.notification_severity_var,
            width=180,
            fg_color=PRIMARY_COLOR,
            button_color=PRIMARY_COLOR,
            button_hover_color=PRIMARY_HOVER
        ).pack(
            anchor="w",
            padx=20,
            pady=(8, 5)
        )

        ctk.CTkLabel(
            notification_card,
            text=(
                "Only threats at or above this "
                "severity will trigger alerts."
            ),
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 20)
        )

        # Notification cooldown

        cooldown_header = ctk.CTkFrame(
            notification_card,
            fg_color="transparent"
        )

        cooldown_header.pack(
            fill="x",
            padx=20
        )

        ctk.CTkLabel(
            cooldown_header,
            text="Notification Cooldown",
            font=FONT_BODY
        ).pack(side="left")

        self.cooldown_label = ctk.CTkLabel(
            cooldown_header,
            text=(
                f"{int(self.notification_cooldown_var.get())}"
                " seconds"
            ),
            font=FONT_BODY,
            text_color=PRIMARY_COLOR
        )

        self.cooldown_label.pack(side="right")

        ctk.CTkSlider(
            notification_card,
            from_=10,
            to=120,
            number_of_steps=22,
            variable=self.notification_cooldown_var,
            command=self.update_cooldown_label,
            progress_color=PRIMARY_COLOR,
            button_color=PRIMARY_COLOR,
            button_hover_color=PRIMARY_HOVER
        ).pack(
            fill="x",
            padx=20,
            pady=(10, 5)
        )

        ctk.CTkLabel(
            notification_card,
            text=(
                "Minimum interval between repeated "
                "alerts for the same file and severity."
            ),
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 20)
        )

    def update_cooldown_label(self, value):

        self.cooldown_label.configure(
            text=f"{int(value)} seconds"
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
            settings["notifications_enabled"] = (
                self.notification_enabled_var.get()
            )

            settings["notification_min_severity"] = (
                self.notification_severity_var.get()
            )

            settings["notification_cooldown"] = int(
                self.notification_cooldown_var.get()
            )

            save_settings(settings)

            apply_notification_settings()

            logger.info(
                "Application preferences updated"
            )

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

        self.notification_enabled_var.set(
            DEFAULT_SETTINGS["notifications_enabled"]
        )

        self.notification_severity_var.set(
            DEFAULT_SETTINGS[
                "notification_min_severity"
            ]
        )

        self.notification_cooldown_var.set(
            DEFAULT_SETTINGS[
                "notification_cooldown"
            ]
        )

        self.update_cooldown_label(
            self.notification_cooldown_var.get()
        )

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
