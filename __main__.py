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
import logging
from functools import wraps
from lmanage.lmanage_handler import LManageHandler
from lmanage.mapview import mapview_execute
from lmanage.utils import logger_creation as log_color

logger = logging.getLogger(__name__)


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
        kwargs = log_args(**kwargs)
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


@lmanage.command()
@click.option("-op", "--output_path",
              help="input your file path to save a tabbed xls of results")
@ click.option("-i", "--ini-file",
               help="Path to the ini file to use for sdk authentication")
@ click.option("-lfp", "--lookml_file_path",
               help="Path folder containing your lookml files, often taken using a git pull from lmanage.your connected lookml project repository")
@ click.option("-t", "--table",
               help="**OPTIONAL** Add a view name to search for elements that rely on this view")
@ click.option("-f", "--field",
               help="**OPTIONAL** Add a fully scoped fieldname (e.g. view_name.field_name) to return a csv with these values")
@ click.option("-l", "--level",
               default='INFO',
               help="**OPTIONAL** Add the value 'DEBUG' to get a more verbose version of the returned stout text")
def mapview(**kwargs):
    level = kwargs.get('level', 'INFO')
    for k, v in kwargs.items():
        if {v} != None:
            logger.info(
                f'You have set {v} for your {k} variable')
        else:
            logger.debug(
                f'There is no value set for {k} please use the `--help` flag to see input parameters')
    mapview_execute.main(**kwargs)
