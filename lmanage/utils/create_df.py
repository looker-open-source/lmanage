import pandas as pd
import json
from pathlib import Path
from coloredlogger import ColoredLogger
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
logger = ColoredLogger()


def create_df(data):
    logger.wtf(type(data))
    data = json.loads(data) if isinstance(data, str) else data
    df = pd.DataFrame(data)
    return df


def check_ini(ini):
    cwd = Path.cwd()

    if ini:
        parsed_ini_file = cwd.joinpath(ini)
    else:
        parsed_ini_file = None

    logger.wtf(parsed_ini_file)
    return parsed_ini_file


check_ini('../../ini/looker.ini')
