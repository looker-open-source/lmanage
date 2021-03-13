import pandas as pd
import json


def create_df(data):
    data = json.loads(data) if isinstance(data, str) else data
    df = pd.DataFrame(data)
    return df
