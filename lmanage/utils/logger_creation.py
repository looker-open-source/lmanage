import logging
from rich.logging import RichHandler
import datetime
import os

def create_timestamp():
    timestamp = datetime.datetime.now()
    unix_ts = timestamp.timestamp()
    trunc_unix_ts = unix_ts - (unix_ts % 60)
    return int(trunc_unix_ts)

def init_logger(dunder_name, testing_mode) -> logging.Logger:
    log_format = (
        '%(asctime)s - '
        '%(name)s - '
        '%(funcName)s - '
        '%(levelname)s - '
        '%(message)s'
    )

    logging.basicConfig(
        format=log_format,
        datefmt=".",
        handlers=[RichHandler()],
    )
    logger = logging.getLogger(dunder_name)

    if testing_mode:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    unix_ts = create_timestamp()

    # Create logs folder if not exists
    os.makedirs('logs', exist_ok=True)
    
    # Output full log
    fh = logging.FileHandler(f'logs/lomt_{unix_ts}.log')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(log_format)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger