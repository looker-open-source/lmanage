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
from lmanage import get_content_with_views


@click.group()
@click.version_option()
def lmanage():
    pass


@lmanage.command()
@click.option("-fp", "--path",
              type=click.Path(exists=True),
              help="input your file path to save a csv of results")
@click.option("-i", "--ini-file",
              help="Path to the ini file to use for sdk authentication")
@click.option("-p", "--project",
              help="Path folder containing your lookml files, often taken using a git pull from your connected lookml project repository")
@click.option("-t", "--table",
              help="Add a view name to search for elements that rely on this view")
@click.option("-f", "--field",
              help="Add a fully scoped fieldname (e.g. view_name.field_name) to return a csv with these values")
def mapview(**kwargs):
    get_content_with_views.main(**kwargs)
