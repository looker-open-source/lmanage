import pandas as pd
import json
from coloredlogger import ColoredLogger
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
logger = ColoredLogger()


def create_df(data):
    logger.wtf(type(data))
    data = json.loads(data) if isinstance(data, str) else data
    df = pd.DataFrame(data)
    return df
