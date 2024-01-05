import logging


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("SimpleSocks5")
    logger.setLevel(logging.DEBUG)

    # Console Handler for logging info and above
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    c_format = logging.Formatter("[%(asctime)s] - [%(levelname)s] - [%(message)s]")
    c_handler.setFormatter(c_format)

    # File Handler for logging errors only
    f_handler = logging.FileHandler("socks_server.log")
    f_handler.setLevel(logging.ERROR)
    f_format = logging.Formatter(
        "[%(asctime)s] - [%(name)s] - [%(levelname)s] - [%(message)s]"
    )
    f_handler.setFormatter(f_format)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger


logger = setup_logger()
