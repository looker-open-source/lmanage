import ast
import logging
import coloredlogs
from time import sleep
import random

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


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

def backoff_jitter(func):
    """
    This decorator adds jitter to a loop.
    Args:
      delay: The delay in seconds.
    Returns:
      A decorator that adds jitter to a loop.
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        jitter_delay = random.uniform(0.3,1.3)
        sleep(jitter_delay)
        print(f' {jitter_delay}')
        return result
    return wrapper

    # def (func):
    #     def wrapper(*args, **kwargs):
    #         for _ in range(int(delay)):
    #             func(*args, **kwargs)
    #             sleep(random.uniform(0, delay))
    #     return wrapper
    # return decorator


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
