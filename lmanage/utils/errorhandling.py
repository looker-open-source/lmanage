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


def return_sleep_message(call_number=0):
    call_number = call_number+1
    sleep_number = 2 ** call_number
    sleep(sleep_number)
    logger.warn(f'Looker is overwhelmed sleeping for {sleep_number} secs')


def dedup_list_of_dicts(input: list):
    stringinput = list(set([str(x) for x in input]))
    deduped = [ast.literal_eval(x) for x in stringinput]
    return deduped


def counter(i=0):
    i += 1
    return i
