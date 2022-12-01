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

import logging
import json
from lmanage.collections import defaultdict
import configparser as ConfigParser
import re
from lmanage.itertools import chain

import coloredlogs
import looker_sdk
from looker_sdk import models
import pandas as pd
from lmanage.utils import parsing_sql
from lmanage.utils import create_df

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')


def find_model_files(proj):
    """Fetches model files from lmanage.PyLookML obj.
    Scans all files in PyLookML object and returns a file
    if that file has a type of Model.

    Args:
        proj: The project from lmanage.PyLookML
    Returns:
        The unparsed model file of a project.
    """
    for file in proj.files():
        path = file.path
        myFile = proj.file(path)
        if myFile.type == 'model':
            return file


def get_view_path(proj):
    """Fetches the file path of a PyLookML Oject.

    Iterates over a list of PyLookML files and returns a list of the files
    if they are of type 'View'
    Args:
        proj: The project from lmanage.PyLookML
    Returns:
        A list of all the file paths pointing towards view objects that are
        kept in a PyLookML object.
        For example:
        ['proj/views/order_items.view.lkml',
        'proj/views/inventory_items.view.lkml',
        'proj/views/products.view.lkml']
    """
    view_list = defaultdict(list)
    for file in proj.files():
        path = file.path
        path = path.split('.')
        if path[-2] == 'view':
            name = file.name.split('.')
            view_list[name[0]].append(file.path)

    return view_list


def fetch_view_files(proj):
    """Fetches the all the named view objects listed in explores of a
    Model file specifically.
    Identifies a model file, iterates over all the explore objects in the
    model file, appends their base view and joined views to a dict object
    Args:
        proj: The project from lmanage.PyLookML
    Returns:
        A dict with key: being the base view and values: list of all the
        used views in the explore object.
        For example:
         defaultdict(<class 'list'>,
         {'order_items':
            ['order_items',
             'order_facts',
             'inventory_items'],
         'events':
            ['events',
             'sessions',
             'session_landing_page']})"""

    true_view_names = defaultdict(list)

    for file in proj.files():
        path = file.path
        myFile = proj.file(path)
        if myFile.type == 'model':
            my_model = file

            for explore in my_model.explores:
                if 'view_name' not in explore and 'from' not in explore:
                    true_view_names[explore.name].append(explore.name)
                if 'view_name' in explore:
                    true_view_names[explore['name']].append(
                        explore['view_name'].value)
                if 'from' in explore:
                    true_view_names[explore['name']].append(
                        explore['from'].value)
                if 'join' in explore:
                    for join in explore['join']:
                        true_view_names[explore['name']].append(join['name'])
                        if 'view_name' in join.__dict__.keys():
                            true_view_names[explore['name']].append(
                                join['view_name'].value)
                        if 'from' in join.__dict__.keys():
                            true_view_names[explore['name']].append(
                                join['from'].value)
    return true_view_names


def get_sql_table_name(proj):
    """Fetches the sql_table_name of view files listed in a PyLookML Oject.

    Iterates over a list of PyLookML files identifies view files aand returns a
    list of the sql_table_names if they exist in an object of type 'View'
    Args:
        proj: The project from lmanage.PyLookML
    Returns:
        A list of all the sql_table_names that are found in a series of view
        objects.
        For example:
        ['public.order_items','public.inventory_items','public.events']
    """
    view_list = defaultdict(list)

    for file in proj.files():
        path = file.path
        myFile = proj.file(path)
        if myFile.type == 'partial_model':
            for view in myFile.views:
                if view.sql_table_name.value:
                    view_list[path].append(view.sql_table_name.value)

    return view_list


def get_sql_table_name_list(sql_table_name_dict, key: True):
    response = []
    for k, v in sql_table_name_dict.items():
        if key:
            response.append(k)
        else:
            response.append(v)

    return response if key else list(chain(*response))


def parse_sql(sdk, qid: int):
    """Idenfies the base tables and joins used by a Looker query.

    Iterates over a list of PyLookML files identifies view files aand returns a
    list of the sql_table_names if they exist in an object of type 'View'
        qid: (int) query_id from lmanage.a  Looker query
        (n.b. NOT THE SAME AS A QID in the url)
    Returns:
        A list of all the tables that are found from lmanage.a Looker generated
        SQL query.
        For example:
        ['public.order_items','public.inventory_items','public.events']
    Exception:
        If a query is broken for whatever reason an Exception is raised to
        continue the program running
    """
    try:
        sql_response = sdk.run_query(query_id=qid, result_format='sql')
        if type(sql_response) == str:
            tables = parsing_sql.extract_tables(sql_response)
            return tables
        else:
            return sql_response
    except looker_sdk.error.SDKError:
        return('No Content')


def get_sql_from_elements(sdk, content_results):
    """Amends returned SDK System__Activity reponse with sql tables used
    from lmanage.the `parse_sql` function.

    Iterates over the response from lmanage.get_dashboards and runs the parse_sql
    function for each returned dashboard element, returns the list of tables
    and amends the dict response and returns it
    Args:
        sdk: Looker SDK object
        content_results: (dict) response from lmanage.get_dashboards function call
    Returns:
        An amended dict response with the sql columns used by each element
        extracted our of the Looker generated SQL for each dashboard object.
        For example:
    [{'dashboard.id': 1,
         'dashboard_element.id': 1,
         'dashboard_element.type': 'vis',
         'dashboard_element.result_source': 'Lookless',
         'query.model': 'bq',
         'query.view': 'order_items',
         'query.formatted_fields': '["order_items.count"]',
         'query.id': 59,
         'dashboard.title': 'dash_1',
         'look.id': None,
         'sql_joins': ['`looker-private-demo.ecomm.order_items`']}]
    """
    for dash in content_results:
        query_id = dash['query.id']
        sql_value = parse_sql(sdk, query_id)

        dash['sql_joins'] = sql_value

    return content_results


def get_dashboards(sdk):
    """Uses the Looker SDK System__Activity model to extract dashboard
    and dashboard_element metadata.

    Simple run_inline_query call to Looker SDK
    Args:
        sdk: Looker SDK object
    Returns:
        An dict response with the dashboard and dashboard_element metadata.
        For example:
    [{'dashboard.id': 1,
         'dashboard_element.id': 1,
         'dashboard_element.type': 'vis',
         'dashboard_element.result_source': 'Lookless',
         'query.model': 'bq',
         'query.view': 'order_items',
         'query.formatted_fields': '["order_items.count"]',
         'query.id': 59,
         'dashboard.title': 'dash_1',
         'look.id': None}]
    """
    query_config = models.WriteQuery(
        model="system__activity",
        view="dashboard",
        fields=[
            "dashboard.id",
            "dashboard_element.id",
            "dashboard_element.type",
            "dashboard_element.result_source",
            "query.model",
            "query.view",
            "query.formatted_fields",
            "query.id",
            "dashboard.title",
            "look.id"
        ],
        filters={
            "dashboard_element.type": "-text",
            "dashboard.deleted_date": "NULL"
        },
        limit='5000'
    )
    query_response = sdk.run_inline_query(
        result_format='json',
        body=query_config
    )

    query_response = json.loads(query_response)

    return query_response


def test_period_appearence(input_response):
    """Checks existence of a period in an input string.

    Simple return True if a period is detected in a string
    Args:
        input_response: (str)
    Returns:
        A boolean response
    For example:
    True or False
    """
    test_period = re.search(r"\.", input_response)
    return bool(test_period)


def match_join_per_query(myresults):
    result = []
    sql_join = myresults['sql_joins']
    sql_table_name = myresults['sql_table_name']

    for sql in sql_join:
        if not bool(test_period_appearence(sql)):
            result.append(sql)
        for name in sql_table_name:
            if sql == name:
                result.append(sql)
    myresults['used_joins'] = result
    return myresults


def all_joins(myresults):
    ''' function returns all used joins for a given set of content '''
    result = []
    for element in range(0, len(myresults)):
        sql_join = myresults[element]['sql_joins']
        sql_table_name = myresults[element]['sql_table_name']

        for sql in sql_join:
            if not bool(test_period_appearence(sql)):
                result.append(sql)
            for name in sql_table_name:
                if sql == name:
                    result.append(sql)
        myresults[element]['used_joins'] = result
    return myresults


def all_views(myresults, proj):
    result = []
    for element in range(0, len(myresults)):
        used_joins = myresults[element]['used_joins']
        for join in used_joins:
            if not bool(test_period_appearence(join)):
                result.append(join)
        for file in proj.files():
            path = file.path
            myFile = proj.file(path)
            if myFile.type != 'model':
                for view in myFile.views:
                    if view.sql_table_name.value in used_joins:
                        result.append(view.name)

    myresults[element]['used_view_names'] = result
    return myresults


def match_views_per_query(myresults, proj):
    result = []
    paths = []
    used_joins = myresults['used_joins']
    for join in used_joins:
        if not bool(test_period_appearence(join)):
            result.append(join)
    for file in proj.files():
        path = file.path
        myFile = proj.file(path)
        if myFile.type != 'model':
            for view in myFile.views:
                if view.sql_table_name.value in used_joins:
                    result.append(view.name)
                    paths.append(path)

    myresults['used_view_names'] = result
    myresults['sql_table_paths_'] = paths
    return myresults


def find_unused_views(myresults):
    used_view_names = sorted(myresults['used_view_names'])
    potential_joins = sorted(myresults['potential_join'])
    result = potential_joins

    for view in used_view_names:
        if view in potential_joins:
            result.remove(view)
    myresults['unused_joins'] = result
    return myresults


def match_view_to_dash(content_results, explore_results, sql_table_name, proj):
    tables_in_explore = []

    sql_table_name_ = get_sql_table_name_list(sql_table_name, key=False)

    for content in content_results:
        result = defaultdict(list)
        result['dashboard_id'] = content['dashboard.id']
        result['element_id'] = content['dashboard_element.id']
        result['sql_joins'] = content['sql_joins']
        result['fields_used'] = content['query.formatted_fields']

        result['sql_table_name'] = sql_table_name_

        for explore, tables in explore_results.items():
            if content['query.view'] == explore:
                result['potential_join'] = tables
                tables_in_explore.append(result)
    return tables_in_explore


def main(**kwargs):
    ini_file = kwargs.get("ini_file")
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read(ini_file)
    project_repo = kwargs.get("project")
    logger.info(f'your project repo is at {project_repo}')
    file_path = kwargs.get("path")
    logger.info(f'your output file is at {file_path}')
    table_mask = kwargs.get("table")
    field_mask = kwargs.get("field")

    create_df.check_ini(ini_file)

    sdk = looker_sdk.init31(config_file=ini_file)
    logger.info

    project = 'legacy_tool_replacing_with_lkml_parser'

    content_results = get_dashboards(sdk)
    logger.debug(f'dashboard_response = {content_results}')
    db_response = get_sql_from_elements(sdk, content_results)
    logger.debug(f'db_response = {db_response}')
    explore_results = fetch_view_files(proj=project)
    logger.debug(f'explore results = {explore_results}')

    sql_table_names = get_sql_table_name(proj=project)
    logger.debug(f'sql_table_names = {sql_table_names}')

    combine = match_view_to_dash(
        db_response, explore_results, sql_table_names, proj=project)
    logger.debug(f'combine = {combine}')

    for element in range(0, len(combine)):
        match_join_per_query(combine[element])
        match_views_per_query(combine[element], project)
        find_unused_views(combine[element])

    df = pd.DataFrame(combine)
    del df['sql_table_name']
    del df['potential_join']
    del df['sql_joins']

    if table_mask is None and field_mask is None:
        logger.info('you have not set any field or table filters')

        df.to_csv(f'{file_path}')
        logger.info(df)

    elif table_mask is not None:
        logger.info(f'your table filter = {table_mask}')

        mask = df['used_view_names'].apply(lambda x: table_mask in x)
        df = df[mask]
        df.to_csv(f'{file_path}')

        logger.info(df)

    elif field_mask is not None:
        logger.info(f'your field filter = {field_mask}')

        mask = df['fields_used'].apply(lambda x: field_mask in x)
