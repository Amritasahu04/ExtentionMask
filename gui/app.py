import customtkinter as ctk

from config import APP_NAME, APP_VERSION
from gui.theme import *
from gui.dashboard import Dashboard


class ExtensionMaskApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(
            f"{APP_NAME} - File Security Monitor"
        )
        self.geometry("1200x750")
        self.minsize(1000, 650)

        self.configure(fg_color=BG_COLOR)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.nav_buttons = {}
        self.current_page = None

        self.create_sidebar()
        self.create_content_area()

        self.show_page("Dashboard")

    def create_sidebar(self):

        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            fg_color=SIDEBAR_COLOR,
            corner_radius=0
        )
        self.sidebar.grid(
            row=0, column=0, sticky="ns"
        )

        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(
            0, weight=1
        )
        self.sidebar.grid_rowconfigure(
            9, weight=1
        )

        # Application branding
        ctk.CTkLabel(
            self.sidebar,
            text="ExtensionMask",
            font=(FONT_FAMILY, 22, "bold"),
            text_color=PRIMARY_COLOR
        ).grid(
            row=0, column=0,
            padx=15, pady=(30, 5)
        )

        ctk.CTkLabel(
            self.sidebar,
            text="File Security Monitor",
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        ).grid(
            row=1, column=0, pady=(0, 30)
        )

        ctk.CTkLabel(
            self.sidebar,
            text="WORKSPACE",
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        ).grid(
            row=2, column=0,
            sticky="w", padx=20, pady=5
        )

        pages = [
            "Dashboard",
            "File Scanner",
            "Live Monitor",
            "Threat Logs",
            "Quarantine",
            "Settings"
        ]

        for index, page in enumerate(pages):

            button = ctk.CTkButton(
                self.sidebar,
                text=page,
                height=42,
                corner_radius=8,
                anchor="w",
                font=FONT_BODY,
                fg_color="transparent",
                hover_color=BORDER_COLOR,
                text_color=TEXT_PRIMARY,
                command=lambda name=page:
                    self.show_page(name)
            )

            button.grid(
                row=index + 3,
                column=0,
                sticky="ew",
                padx=12, pady=4
            )

            self.nav_buttons[page] = button

        # Version information
        ctk.CTkLabel(
            self.sidebar,
            text=f"Version {APP_VERSION}",
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY
        ).grid(
            row=10, column=0, pady=(5, 20)
        )

    def create_content_area(self):

        self.content = ctk.CTkFrame(
            self,
            fg_color=BG_COLOR,
            corner_radius=0
        )
        self.content.grid(
            row=0, column=1,
            sticky="nsew", padx=25, pady=20
        )

        self.content.grid_columnconfigure(
            0, weight=1
        )
        self.content.grid_rowconfigure(
            0, weight=1
        )

    def show_page(self, page_name):

        # Highlight selected navigation button
        for name, button in self.nav_buttons.items():

            button.configure(
                fg_color=(
                    PRIMARY_COLOR
                    if name == page_name
                    else "transparent"
                )
            )

        # Remove previous page
        if self.current_page is not None:
            self.current_page.destroy()

        # Load selected page
        if page_name == "Dashboard":

            self.current_page = Dashboard(
                self.content
            )

        else:

            self.current_page = (
                self.create_placeholder(page_name)
            )

        self.current_page.grid(
            row=0, column=0,
            sticky="nsew"
        )

    def create_placeholder(self, page_name):

        frame = ctk.CTkFrame(
            self.content,
            fg_color=BG_COLOR
        )

        ctk.CTkLabel(
            frame,
            text=page_name,
            font=FONT_TITLE,
            text_color=TEXT_PRIMARY
        ).pack(
            anchor="w", pady=(10, 20)
        )

        ctk.CTkLabel(
            frame,
            text="This module is under development.",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY
        ).pack(expand=True)

        return frame
