import ast
import logging
from looker_sdk import error
from time import sleep

logger = logging.getLogger(__name__)


def calc_done_percent(iterator: int, total: int) -> str:
    percent = (iterator/total) * 100
    return f'{int(percent)} %'


def return_error_message(input: str):
    # err_response = input.args[0]
    # err_response = json.loads(err_response)
    if len(input.errors) == 0:
        err_response = input.message
    else:
        err_response = input.errors[0].message

    return err_response

def test_object_data(object: list) -> bool:
    if object:
        return True
    else:
        return False

def user_authentication_test(sdk) -> bool:
    try:
        sdk.me()
        return True
    except error.SDKError():
        return False
    
def return_sleep_message(call_number=0, quiet=False):
    call_number = call_number+1
    sleep_number = 2 ** call_number
    sleep(sleep_number)
    if not quiet:
        logger.warn(f'Looker is overwhelmed sleeping for {sleep_number} secs')


def dedup_list_of_dicts(input: list):
    stringinput = list(set([str(x) for x in input]))
    deduped = [ast.literal_eval(x) for x in stringinput]
    return deduped


def counter(i=0):
    i += 1
    return i
