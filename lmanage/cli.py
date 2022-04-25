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
import coloredlogs
import logging
import click
from lmanage.mapview import get_content_with_views
from lmanage.configurator import provision_instance_permission_structure

logger = logging.getLogger(__name__)


@click.group()
@click.version_option()
def lmanage():
    pass


@lmanage.command()
@click.option("-fp", "--path",
              help="input your file path to save a csv of results")
@ click.option("-i", "--ini-file",
               help="Path to the ini file to use for sdk authentication")
@ click.option("-p", "--project",
               help="Path folder containing your lookml files, often taken using a git pull from your connected lookml project repository")
@ click.option("-t", "--table",
               help="**OPTIONAL** Add a view name to search for elements that rely on this view")
@ click.option("-f", "--field",
               help="**OPTIONAL** Add a fully scoped fieldname (e.g. view_name.field_name) to return a csv with these values")
@ click.option("-l", "--level",
               default='INFO',
               help="**OPTIONAL** Add the value 'DEBUG' to get a more verbose version of the returned stout text")
def mapview(**kwargs):
    level = kwargs.get('level', 'INFO')
    coloredlogs.install(level=level, logger=logger)
    for k, v in kwargs.items():
        if {v} != None:
            logger.info(
                f'You have set {v} for your {k} variable')
        else:
            logger.debug(
                f'There is no value set for {k} please use the `--help` flag to see input parameters')
    get_content_with_views.main(**kwargs)


@lmanage.command()
@ click.option("-i", "--ini-file",
               help="**OPTIONAL ** Specify API Credentials in an ini file, if no path is given program will assume these values are set as environmental variables as denoted at https: // github.com/looker-open-source/sdk-codegen  # environment-variable-configuration")
@ click.option("-yp", "--yaml-config-path",
               help="Path to the yaml file to use for instance configuration")
@ click.option("-l", "--level",
               default='INFO',
               help="**OPTIONAL** Add the value 'DEBUG' to get a more verbose version of the returned stout text")
def configurator(**kwargs):
    level = kwargs.get('level', 'INFO')
    coloredlogs.install(level=level, logger=logger)
    for k, v in kwargs.items():
        if {v} != None:
            logger.info(
                f'You have set {v} for your {k} variable')
        else:
            logger.debug(
                f'There is no value set for {k} please use the `--help` flag to see input parameters')
    provision_instance_permission_structure.main(**kwargs)


# @instance_config.command()
# @click.option("-t", "--test")
# .configurator.configura.configuratortor def update_configs(**kwargs):
#     print(kwargs.items())


# @instance_config.command()
# @click.option("-t", "--test")
# def user_permissions(**kwargs):
#     print('users')


# @instance_config.command()
# @click.option("-t", "--test")
# def full_instance_config(**kwargs):
#     print('full')
