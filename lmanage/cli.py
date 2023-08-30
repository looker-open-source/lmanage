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
import configparser
import os
from functools import wraps
from lmanage.capturator.looker_api_reader import LookerApiReader
from lmanage.capturator.looker_config_saver import LookerConfigSaver
from lmanage.configurator.looker_config_reader import LookerConfigReader
from lmanage.configurator.looker_provisioner import LookerProvisioner
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
                  help='Add this flag to get a more verbose version of the returned stout text.')
    @click.option('-f', '--force',
                  is_flag=True,
                  help='Add this flag to skip confirmation prompt for capturing and configuring instance.')
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
    ini_file, config_dir, verbose, force = kwargs.get('ini_file'), kwargs.get(
        'config_dir'), kwargs.get('verbose'), kwargs.get('force')

    try:
        target_url = get_target_url(ini_file)
        if force or (not force and click.confirm(f'\nYou are about to capture settings and content from instance {target_url}. Proceed?')):
            config = LookerApiReader(ini_file).get_config()
            LookerConfigSaver(config_dir).save(config)
    except RuntimeError as e:
        print(e)


@lmanage.command()
@common_options
def configurator(**kwargs):
    """Configures security settings for your looker instance"""
    ini_file, config_dir, verbose, force = kwargs.get('ini_file'), kwargs.get(
        'config_dir'), kwargs.get('verbose'), kwargs.get('force')

    try:
        target_url = get_target_url(ini_file)
        config_reader = LookerConfigReader(config_dir)
        config_reader.read()
        summary = config_reader.get_summary()
        if force or (not force and click.confirm(f'\nYou are about configure instance {target_url} with:\n{summary}\nAre you sure you want to proceed?')):
            LookerProvisioner(ini_file).provision(config_reader.config)
    except RuntimeError as e:
        print(e)


def get_target_url(ini_file):
    if ini_file:
        config_parser = configparser.ConfigParser()
        successful_read = config_parser.read(ini_file)

        if not successful_read:
            raise FileNotFoundError(
                f'Configuration file "{ini_file}" not found.')

        sections = config_parser.sections()
        return config_parser.get(sections[0], 'base_url')
    else:
        target_url = os.getenv('LOOKERSDK_BASE_URL')
        if target_url is None:
            raise ValueError(
                'LOOKERSDK_BASE_URL environment variable not set.')


if __name__ == '__main__':
    lmanage()
