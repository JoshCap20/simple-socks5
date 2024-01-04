import logging


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("socks_server")
    logger.setLevel(logging.DEBUG)

    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler("socks_server.log")
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.ERROR)

    c_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger


logger: logging.Logger = setup_logger()
