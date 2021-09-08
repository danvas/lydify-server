import logging


def get_logger(name: str, debug: bool = False) -> logging.Logger:
    logger = logging.getLogger(name)
    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level=level)

    return logger

