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
from lmanage import provision_instance_permission_structure

logger = logging.getLogger(__name__)


@click.group(name='configurator')
def configurator():
    """Configures security settings for your looker instance"""
    pass


@configurator.command()
@ click.option("-i", "--ini-file",
               help="**OPTIONAL ** Specify API Credentials in an ini file, if no path is given program will assume these values are set as environmental variables as denoted at https: // github.com/looker-open-source/sdk-codegen  # environment-variable-configuration")
@ click.option("-yp", "--yaml-config-path",
               help="Path to the yaml file to use for instance configuration")
@ click.option("-l", "--level",
               default='INFO',
               help="**OPTIONAL** Add the value 'DEBUG' to get a more verbose version of the returned stout text")
def configurator(**kwargs):
    """Configures security settings for your looker instance"""
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
