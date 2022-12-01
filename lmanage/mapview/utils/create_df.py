"""
Copyright 2021 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
import logging
from lmanage.pathlib import Path
import json
import pandas as pd

logger = logging.getLogger(__name__)


def create_df(data):
    logger.debug(type(data))
    data = json.loads(data) if isinstance(data, str) else data
    df = pd.DataFrame(data)
    return df


def check_ini(ini):
    cwd = Path.cwd()

    if ini:
        parsed_ini_file = cwd.joinpath(ini)
    else:
        parsed_ini_file = None

    if os.path.isfile(parsed_ini_file):
        logger.info(f'opening your ini file at {parsed_ini_file}')
        return parsed_ini_file
    else:
        logger.debug(
            f'the path to your ini file is not valid at {parsed_ini_file}')
