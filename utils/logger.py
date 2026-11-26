import logging

from logging.handlers import RotatingFileHandler

from config import LOG_FILE, initialize_directories


def setup_logging():

    initialize_directories()

    root_logger = logging.getLogger()

    root_logger.setLevel(logging.INFO)

    for handler in root_logger.handlers:

        if getattr(
            handler,
            "_extensionmask_handler",
            False
        ):
            return root_logger

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | "
            "%(levelname)-8s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=2 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    file_handler._extensionmask_handler = True

    root_logger.addHandler(file_handler)

    root_logger.info(
        "ExtensionMask logging initialized"
    )

    return root_logger


def get_logger(name):

    return logging.getLogger(name)
