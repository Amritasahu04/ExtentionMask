import customtkinter as ctk

from database.db import (
    get_statistics,
    get_threat_history
)

from gui.theme import *


class Dashboard(ctk.CTkScrollableFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=BG_COLOR,
            corner_radius=0
        )

        self.grid_columnconfigure(0, weight=1)

        self.build_dashboard()

    def build_dashboard(self):

        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        stats = get_statistics()

        # Page header
        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header.grid(
            row=0, column=0,
            sticky="ew", pady=(5, 20)
        )

        ctk.CTkLabel(
            header,
            text="Dashboard",
            font=FONT_TITLE,
            text_color=TEXT_PRIMARY
        ).pack(side="left")

        ctk.CTkButton(
            header,
            height=BUTTON_HEIGHT,
            corner_radius=BUTTON_RADIUS,
            font=FONT_BUTTON,
            text="Refresh",
            width=100,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            command=self.build_dashboard
        ).pack(side="right")

        ctk.CTkLabel(
            self,
            text="File security overview and threat analysis",
            font=FONT_SUBTITLE,
            text_color=TEXT_SECONDARY
        ).grid(
            row=1, column=0,
            sticky="w", pady=(0, 20)
        )

        # Statistics cards
        cards = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        cards.grid(
            row=2, column=0,
            sticky="ew", pady=(0, 20)
        )

        for column in range(4):
            cards.grid_columnconfigure(
                column, weight=1,
                uniform="cards"
            )

        card_data = [
            (
                "Total Scans",
                stats["total_scans"],
                PRIMARY_COLOR
            ),
            (
                "No Identified Risk",
                stats["no_risk"],
                SUCCESS_COLOR
            ),
            (
                "Flagged Scans",
                stats["suspicious"],
                DANGER_COLOR
            ),
            (
                "Unknown",
                stats["unknown"],
                TEXT_SECONDARY
            )
        ]

        for index, data in enumerate(card_data):
            self.create_stat_card(
                cards, index, *data
            )

        # Threat distribution
        distribution = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=CARD_RADIUS,
            border_width=1,
            border_color=BORDER_COLOR
        )
        distribution.grid(
            row=3, column=0,
            sticky="ew", pady=(0, 20)
        )

        ctk.CTkLabel(
            distribution,
            text="Threat Distribution",
            font=FONT_HEADING,
            text_color=TEXT_PRIMARY
        ).pack(
            anchor="w", padx=20, pady=15
        )

        levels = [
            ("Low", stats["low"], LOW_COLOR),
            ("Medium", stats["medium"], WARNING_COLOR),
            ("High", stats["high"], HIGH_COLOR),
            ("Critical", stats["critical"], DANGER_COLOR)
        ]

        total = max(stats["suspicious"], 1)

        for level, count, color in levels:

            row = ctk.CTkFrame(
                distribution,
                fg_color="transparent"
            )
            row.pack(
                fill="x", padx=20, pady=8
            )

            ctk.CTkLabel(
                row,
                text=level,
                width=80,
                anchor="w",
                font=FONT_BODY
            ).pack(side="left")

            progress = ctk.CTkProgressBar(
                row,
                progress_color=color,
                fg_color=BORDER_COLOR,
                height=10
            )
            progress.pack(
                side="left",
                fill="x",
                expand=True,
                padx=15
            )
            progress.set(count / total)

            ctk.CTkLabel(
                row,
                text=str(count),
                width=35,
                font=FONT_BODY
            ).pack(side="right")

        # Recent threats
        recent = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=CARD_RADIUS,
            border_width=1,
            border_color=BORDER_COLOR
        )
        recent.grid(
            row=4, column=0,
            sticky="ew", pady=(0, 20)
        )

        ctk.CTkLabel(
            recent,
            text="Recent Security Findings",
            font=FONT_HEADING,
            text_color=TEXT_PRIMARY
        ).pack(
            anchor="w", padx=20, pady=15
        )

        threats = get_threat_history(limit=5)

        if not threats:
            ctk.CTkLabel(
                recent,
                text="No security findings recorded.",
                font=FONT_BODY,
                text_color=TEXT_SECONDARY
            ).pack(pady=20)

        for threat in threats:
            self.create_threat_row(recent, threat)

    def create_stat_card(
        self, parent, column, title, value, color
    ):

        card = ctk.CTkFrame(
            parent,
            fg_color=CARD_COLOR,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR
        )
        card.grid(
            row=0, column=column,
            sticky="nsew", padx=5
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        ).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        ctk.CTkLabel(
            card,
            text=str(value),
            font=FONT_STAT,
            text_color=color
        ).pack(
            anchor="w", padx=15, pady=(0, 15)
        )

    def create_threat_row(self, parent, threat):

        row = ctk.CTkFrame(
            parent,
            fg_color=BG_COLOR,
            corner_radius=8
        )
        row.pack(
            fill="x", padx=20, pady=5
        )

        details = ctk.CTkFrame(
            row,
            fg_color="transparent"
        )
        details.pack(
            side="left", padx=15,
            pady=10, fill="x", expand=True
        )

        ctk.CTkLabel(
            details,
            text=threat["filename"],
            font=FONT_BODY,
            text_color=TEXT_PRIMARY,
            wraplength=400,
            justify="left"
        ).pack(anchor="w")

        findings = ", ".join(
            threat.get("findings", [])
        )

        ctk.CTkLabel(
            details,
            text=findings,
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY,
            wraplength=400,
            justify="left"
        ).pack(anchor="w")

        severity = threat["severity"]

        ctk.CTkLabel(
            row,
            text=severity,
            font=FONT_BODY,
            text_color=SEVERITY_COLORS.get(
                severity, TEXT_SECONDARY
            )
        ).pack(
            side="right", padx=15
        )
