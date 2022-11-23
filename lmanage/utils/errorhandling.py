import json
import logging
import coloredlogs
from time import sleep

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


def return_error_message(input: str):
    err_response = input.args[0]
    err_response = json.loads(err_response)
    err_response = err_response.get('errors')[0].get('message')
    return err_response


def return_sleep_message():
    sleep(3)
    logger.warn('Looker is overwhelmed sleeping for 3 secs')
