import lkml
import sqlparse
import looker_sdk
from looker_sdk import models
import json
from pathlib import Path
from collections import defaultdict
import pandas as pd
import lookml
import configparser as ConfigParser
import snoop
import re
from itertools import chain
from lmanage.utils import parsing_sql
from lmanage.utils import create_df
from coloredlogger import ColoredLogger
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
logger = ColoredLogger()


def find_model_files(proj):
    for file in proj.files():
        path = file.path
        myFile = proj.file(path)
        if myFile.type == 'model':
            return file


def get_view_path(proj):
    view_list = defaultdict(list)
    for file in proj.files():
        path = file.path
        path = path.split('.')
        if path[-2] == 'view':
            name = file.name.split('.')
            view_list[name[0]].append(file.path)

    return view_list


def fetch_view_files(proj):
    file = find_model_files(proj)
    true_view_names = defaultdict(list)
    for explore in file.explores:
        if 'view_name' not in explore and 'from' not in explore:
            true_view_names[explore.name].append(explore.name)
        if 'view_name' in explore:
            true_view_names[explore['name']].append(
                explore['view_name'].value)
        if 'from' in explore:
            true_view_names[explore['name']].append(explore['from'].value)
        if 'join' in explore:
            for join in explore['join']:
                true_view_names[explore['name']].append(join['name'])
                if 'view_name' in join:
                    true_view_names[explore['name']].append(join['view_name'])
                if 'from' in join:
                    true_view_names[explore['name']].append(join['from'])
    return true_view_names


def get_sql_table_name(proj):
    response = []
    for file in proj.files():
        path = file.path
        myFile = proj.file(path)
        if myFile.type == 'partial_model':
            for view in myFile.views:
                if view.sql_table_name.value:
                    response.append(view.sql_table_name.value)

    return response


def parse_sql(sdk, qid: int):
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
    for dash in content_results:
        query_id = dash['query.id']
        sql_value = parse_sql(sdk, query_id)

        dash['sql_joins'] = sql_value

    return content_results


def get_dashboards(sdk):
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
            "dashboard_element.type": "-text"
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
        logger.wtf(f'result= {result}')
        myresults[element]['used_joins'] = result
        logger.wtf(myresults)
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

    myresults['used_view_names'] = result
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

    for content in content_results:
        result = defaultdict(list)
        result['dashboard_id'] = content['dashboard.id']
        result['element_id'] = content['dashboard_element.id']
        result['sql_joins'] = content['sql_joins']
        result['fields_used'] = content['query.formatted_fields']

        result['sql_table_name'] = sql_table_name

        for explore, tables in explore_results.items():
            if content['query.view'] == explore:
                result['potential_join'] = tables
                tables_in_explore.append(result)
    return tables_in_explore


# @snoop
def main(**kwargs):
    cwd = Path.cwd()
    ini_file = kwargs.get("ini_file")
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read(ini_file)
    project_repo = kwargs.get("project")
    logger.success(f'your project repo is at {project_repo}')
    file_path = kwargs.get("path")
    logger.success(f'your output file is at {file_path}')
    table_mask = kwargs.get("table")
    field_mask = kwargs.get("field")

    create_df.check_ini(ini_file)

    sdk = looker_sdk.init31(config_file=ini_file)

    project = lookml.Project(
        path=project_repo
    )

    content_results = get_dashboards(sdk)
    db_response = get_sql_from_elements(sdk, content_results)
    explore_results = fetch_view_files(proj=project)
    sql_table_names = get_sql_table_name(proj=project)

    combine = match_view_to_dash(
        db_response, explore_results, sql_table_names, proj=project)
    for element in range(0, len(combine)):
        match_join_per_query(combine[element])
        match_views_per_query(combine[element], project)
        find_unused_views(combine[element])

    df = pd.DataFrame(combine)

    if table_mask == None and field_mask == None:
        logger.success('you have not set any field or table filters')

        df.to_csv(f'{file_path}')
        logger.success(df)

    elif table_mask != None:
        logger.success(f'your table filter = {table_mask}')

        mask = df['used_view_names'].apply(lambda x: table_mask in x)
        df = df[mask]
        df.to_csv(f'{file_path}')

        logger.success(df)

    elif field_mask != None:
        logger.success(f'your field filter = {field_mask}')

        mask = df['fields_used'].apply(lambda x: field_mask in x)
        df = df[mask]
        df.to_csv(f'{file_path}')

        logger.success(df)


if __name__ == "__main__":
    main(ini_file="/usr/local/google/home/hugoselbie/code_sample/py/projects/ini/k8.ini",
         project="/usr/local/google/home/hugoselbie/code_sample/py/projects/lmanage/tests/test_lookml_files/the_look",
         path="/usr/local/google/home/hugoselbie/code_sample/py/projects/lmanage/tests/test_lookml_files/the_look")
