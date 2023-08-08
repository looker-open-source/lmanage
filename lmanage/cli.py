#!/usr/bin/python
#
# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import click
from functools import wraps
from lmanage.lmanage_handler import LManageHandler
from lmanage.utils import logger_creation as log_color

logger = log_color.init_logger(__name__, testing_mode=False)


@click.group()
@click.version_option()
def lmanage():
    pass


def log_args(**kwargs):
    log_level = kwargs.get('verbose', False)
    logger = log_color.init_logger(__name__, testing_mode=log_level)
    for k, v in kwargs.items():
        if {v} != None:
            logger.info(
                f'You have set {v} for your {k} variable')
        else:
            logger.debug(
                f'There is no value set for {k} please use the `--help` flag to see input parameters.')


def clean_args(**kwargs):
    kwargs['config_dir'] = kwargs['config_dir'].rstrip('/')
    return kwargs


def common_options(f):
    @click.option('-i', '--ini-file',
                  help='Specify API Credentials in an ini file, if no path is given program will assume these values are set as environmental variables as denoted at https://github.com/looker-open-source/sdk-codegen#environment-variable-configuration.')
    @click.option('-cd', '--config-dir',
                  help='Where to save the YAML files to use for instance configuration.', required=True)
    @click.option('-v', '--verbose',
                  is_flag=True,
                  help='Add this flag value to get a more verbose version of the returned stout text.')
    @click.pass_context
    @wraps(f)
    def decorated_function(ctx, *args, **kwargs):
        log_args(**kwargs)
        kwargs = clean_args(**kwargs)
        return ctx.invoke(f, *args, **kwargs)
    return decorated_function


@lmanage.command()
@common_options
def capturator(**kwargs):
    """Captures security settings for your looker instance"""
    LManageHandler(kwargs.get(
        'ini_file'), kwargs.get('config_dir')).capture()


@lmanage.command()
@common_options
def configurator(**kwargs):
    """Configures security settings for your looker instance"""
    LManageHandler(kwargs.get(
        'ini_file'), kwargs.get('config_dir')).configure()


if __name__ == '__main__':
    lmanage()
