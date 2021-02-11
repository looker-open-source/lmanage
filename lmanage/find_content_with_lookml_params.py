import looker_sdk
import pandas as pd
import glob
import lkml
import json
import configparser as ConfigParser
from github import Github
import base64
import csv
import argparse


def github_lkml(repo_name: str):
    """connect to repo with lookml, iterate through lookml and returns list
    of parsed lookml

    Args:
        repo_name (str): name of repo (not path)

    Returns:
        [list]: list of lookml elements in repo
    """
    g = Github(github_token)

    repo = g.get_repo(repo_name)

    contents = repo.get_contents("", ref='master')
    print(contents)
    lookml = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            x = base64.b64decode(file_content.content).decode('UTF-8')
            try:
                lookml.append(lkml.load(x))
            except SyntaxError:
                print(f'''you have a lookml syntax error in {file_content}
                and your file cannot be parsed
                ''')

    return lookml


def path_file_parser(path: str, extension: str, recursive=True):
    """Return a list of Full File Paths
    Parameters:
    path (str): Parent Directory to parse
    extension (Optional) (str): fil e extension to search, i.e. ".txt"
    recursive (Boolan): Defaults to false to check child directories
    """
    return [f for f in glob.glob(path + "**/*" + extension, recursive=recursive)]


def file_parse_lkml(file_paths: list):
    """Iterate through local file paths
    and return a list of lookml files with an element
    for each lookml file]

    Args:
        file_paths (list): [a list of local path strings]

    Returns:
        [list]: [list of parsed lookml]
    """
    response_list = []
    for path in file_paths:
        with open(path, 'r') as file:
            response_list.append(lkml.load(file))

    return response_list


def find_param_lkml_objects(lookml_list: list, param: str):
    """[summary]

    Args:
        lookml_list (list): [description]

    Returns:
        [type]: [description]
    """
    html_elements = {}

    for lookml_object in lookml_list:
        parsed = lookml_object
        try:
            parsed['views']

            view_name = parsed['views'][0]['name']

            elements = ['dimension_groups', 'dimensions', 'measures']
            fields = []

            for lkml_element in parsed['views'][0].keys():
                if lkml_element in elements:

                    for obj in parsed['views'][0][lkml_element]:
                        if param in obj.keys():
                            fields.append(view_name+'.'+obj['name'])
            html_elements[view_name] = fields
        except KeyError:
            pass
    return html_elements


def compare_html_objects(queryCompare: dict):
    queryParams = looker_sdk.models.WriteQuery(
        model='system__activity',
        view='dashboard',
        fields=[
            "dashboard.count",
            "filtered_history_dashboards.dashboards_used_last_30",
            "dashboard.title",
            "dashboard.id",
            "dashboard_element.title",
            "query.formatted_fields"
            ],
        dynamic_fields="[{\"table_calculation\":\"used_dashboards\",\"label\":\"Used Dashboards\",\"expression\":\"${filtered_history_dashboards.dashboards_used_last_30}\",\"value_format\":null,\"value_format_name\":null,\"_kind_hint\":\"measure\",\"_type_hint\":\"number\",\"is_disabled\":true},{\"table_calculation\":\"unused_dashboards\",\"label\":\"Unused Dashboards\",\"expression\":\"${dashboard.count} - ${filtered_history_dashboards.dashboards_used_last_30}\",\"value_format\":null,\"value_format_name\":null,\"_kind_hint\":\"measure\",\"_type_hint\":\"number\"}]",
        limit='5000'
        )

    response = sdk.run_inline_query(result_format='json', body=queryParams)
    df = json.loads(response)

    df = pd.DataFrame(df)
    df = df[(df['unused_dashboards'] == 0)]

    functionResponse = []

    file = open('content_check.csv', 'w', newline='')
    with file:

        header = ['Dashboard Title', 'Dashboard ID', 'Element Title']
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()

        for row in df.itertuples():
            fields = row[4]
            try:
                fields = json.loads(fields)
                for field in fields:
                    for view, dimensions in queryCompare.items():
                        for dim in dimensions:
                            if dim == field:
                                functionResponse.append(
                                    f'''dashboard title = {row[1]},
                                    dashboard id = {row[2]},
                                    element title = {row[3]}'''
                                    )
                                writer.writerow({
                                    'Dashboard Title': row[1],
                                    'Dashboard ID': row[2],
                                    'Element Title': row[3]
                                })
                            else:
                                pass

            except TypeError:
                pass

    print(functionResponse)


if __name__ == "__main__":
    """
    Command line parser arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--ini', type=str)
    parser.add_argument('--repo', type=str)
    parser.add_argument('--lookml_param', type=str)
    args = parser.parse_args()

    ini_file = args.ini

    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read(ini_file)

    github_token = config.get('Github', 'github_token')
    sdk = looker_sdk.init31(config_file=ini_file)
    gitoutput = github_lkml(args.repo)
    html_objects = find_param_lkml_objects(lookml_list=gitoutput, param=args.lookml_param)
    compare_html_objects(queryCompare=html_objects)

    # print(compare_html_objects)
    # s(queryCompare=find_html_lkml_objects(lookml_list=github_lkml('monkey100'))))
