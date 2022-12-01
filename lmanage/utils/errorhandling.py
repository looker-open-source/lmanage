import ast
import logging
import coloredlogs
from time import sleep


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


def return_error_message(input: str):
    # err_response = input.args[0]
    # err_response = json.loads(err_response)
    if len(input.errors) == 0:
        err_response = input.message
    else:
        err_response = input.errors[0].message
    return err_response


def return_sleep_message():
    sleep(3)
    logger.warn('Looker is overwhelmed sleeping for 3 secs')


def dedup_list_of_dicts(input: list):
    stringinput = list(set([str(x) for x in input]))
    deduped = [ast.literal_eval(x) for x in stringinput]
    return deduped
