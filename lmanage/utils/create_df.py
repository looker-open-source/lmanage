import warnings
from coloredlogger import ColoredLogger
from pathlib import Path
import json
import pandas as pd
import os
warnings.simplefilter(action='ignore', category=FutureWarning)
logger = ColoredLogger()


def create_df(data):
    logger.wtf(type(data))
    data = json.loads(data) if isinstance(data, str) else data
    df = pd.dataframe(data)
    return df


def check_ini(ini):
    cwd = Path.cwd()

    if ini:
        parsed_ini_file = cwd.joinpath(ini)
    else:
        parsed_ini_file = none

    if os.path.isfile(parsed_ini_file):
        logger.success(f'opening your ini file at {parsed_ini_file}')
        return parsed_ini_file
    else:
        logger.wtf(
            f'the path to your ini file is not valid at {parsed_ini_file}')


if __name__ == '__main__':

    check_ini('../ini/k8.ini')
