import customtkinter as ctk

from config import initialize_directories
from database.db import initialize_database
from gui.app import ExtensionMaskApp
from utils.logger import setup_logging

def main():

    initialize_directories()
    initialize_database()

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ExtensionMaskApp()
    app.mainloop()


if __name__ == "__main__":
    setup_logging()
    main()
