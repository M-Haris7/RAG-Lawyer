import logging

def setup_logger(name="RAG"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] ----- [%(message)s]")
    console_handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()

logger.info("RAG process started")
logger.debug("Debugging")
logger.critical("Critical message")
logger.error("Failed to load")