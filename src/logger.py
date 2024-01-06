import logging


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


def get_logger(name: str, verbose=True) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Console Handler for logging info and above
    c_handler = logging.StreamHandler()
    console_level = logging.DEBUG if verbose else logging.INFO
    c_handler.setLevel(console_level)
    c_format = ColorFormatter("[%(asctime)s] - [%(levelname)s] - %(message)s")
    c_handler.setFormatter(c_format)

    # File Handler for logging errors only
    f_handler = logging.FileHandler("errors.log")
    f_handler.setLevel(logging.ERROR)
    f_format = logging.Formatter(
        "[%(asctime)s] - [%(name)s] - [%(levelname)s] - [%(message)s]"
    )
    f_handler.setFormatter(f_format)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger
