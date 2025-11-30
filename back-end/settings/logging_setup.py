import logging
import os


def setup_logger():
    log_level = os.getenv("LOG_LEVEL")
    LOG_LEVEL = logging.getLevelNamesMapping()[log_level or "INFO"]
    logger = logging.getLogger()
    logger_handler = logging.StreamHandler()
    logger.addHandler(logger_handler)
    logger_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s: %(name)s, %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logging.root.setLevel(LOG_LEVEL)
