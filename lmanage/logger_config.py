import logging


def setup_logger():
    # Create a custom logger
    logger = logging.getLogger(__name__)

    # Set the level of logging.
    # You might want to use logging.DEBUG or logging.ERROR in other scenarios
    logger.setLevel(logging.INFO)

    # Create handlers. Here, we create a StreamHandler (for stdout) and a FileHandler (for writing logs to a file)
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('file.log')
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.ERROR)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger
