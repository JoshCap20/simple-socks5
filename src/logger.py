import logging
from logging.handlers import RotatingFileHandler

from .config import ProxyConfiguration


class LogColors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    WHITE = "\033[97m"
    GREY = "\033[90m"
    RESET = "\033[0m"


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.ERROR: LogColors.RED,
        logging.WARNING: LogColors.YELLOW,
        logging.INFO: LogColors.WHITE,
        logging.DEBUG: LogColors.GREY,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno)
        message = super().format(record)
        if color:
            message = color + message + LogColors.RESET
        return message


_loggers = {}


def get_logger(name: str) -> logging.Logger:
    if name not in _loggers:
        logger = logging.getLogger(name)

        if ProxyConfiguration.is_initialized():
            configure_logger(logger)
        else:
            logger.addHandler(logging.NullHandler())

        _loggers[name] = logger

    return _loggers[name]


def configure_logger(logger: logging.Logger) -> None:
    logging_level = ProxyConfiguration.get_logging_level()

    logger.setLevel(logging.DEBUG)

    if logging_level != logging.NOTSET:
        # Console Handler for logging
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging_level)
        c_format = ColorFormatter("[%(asctime)s] - [%(levelname)s] - %(message)s")
        c_handler.setFormatter(c_format)

        # File Handler for logging errors only
        log_file_size: int = 1048576  # 1 MB
        f_handler = RotatingFileHandler(
            "errors.log", maxBytes=log_file_size, backupCount=5
        )
        f_handler.setLevel(logging.ERROR)
        f_format = logging.Formatter(
            "[%(asctime)s] - [%(name)s] - [%(levelname)s] - [%(message)s]"
        )
        f_handler.setFormatter(f_format)

        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
    else:
        logger.addHandler(logging.NullHandler())


def update_loggers() -> None:
    for logger in _loggers.values():
        configure_logger(logger)
