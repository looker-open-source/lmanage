from looker_sdk import models, error
import looker_sdk
import configparser as ConfigParser
import json
import csv
import os
import subprocess
import datetime
from coloredlogger import ColoredLogger
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
logger = ColoredLogger()


GZR_INSTANCE_NAME = 'profservices.dev.looker.com'


def backupDir(content_type: str):
    """function to generate backup directories

    Args:
        content_type (str): dashboard/look switch
    """
    path = 'dashboard_backup' if content_type == 'dashboard' else 'look_backup'

    if not os.path.exists(path):
        os.mkdir(path)
        print(f"Successfully created the directory {path}")
    elif not os.path.isdir(path):
        print(f"Creation of the directory {path} has failed")


def get_last_accessed_content_dates(content_type: str, delinquent_days: int):
    query_config = models.WriteQuery(
        model="system__activity",
        view="content_usage",
        fields=[
            "content_usage.last_accessed_date",
            "content_usage.content_id",
            "content_usage.content_title",
            "content_usage.content_type"
        ],
        filters={
            "content_usage.last_accessed_date": f"before {delinquent_days} days ago",
            "content_usage.content_type": content_type
        },
        limit=' 5000'
    )
    query_response = sdk.run_inline_query(
        result_format='json',
        body=query_config
    )
    query_response = json.loads(query_response)

    return query_response


# def test(days: int):
#     content_types = ['Look', 'Dashboard']
#     for content in content_types:
#         content_response = get_last_accessed_content_dates(content_type: content, delinquent_days: days)
#         for content_type in range(0, len(content_response)):
#             if content == 'Look':
#                 pass


def deliquent_content(content_type: str, delinquent_days: int):
    """identify content with delinquent days of x. passed into api call for run inline query
    this input is then used to both delete the content and use gzr to export the json
    content rendering for easy restoration after delete

    Args:
        content_type (str): [dashboard/look switch]
        delinquent_days (int): [days]

    Returns:
        [type]: [list of id's that are deleted]
    """
    if content_type == 'dashboard':
        backupDir('dashboard')
        delinquent_dashboards = []
        dashboard_response = get_last_accessed_content_dates(
            content_type=content_type,
            delinquent_days=delinquent_days
        )

        for dashboard in range(0, len(dashboard_response)):
            delinquent_dashboards.append(
                dashboard_response[dashboard]['content_usage.content_id'])
            subprocess.run(
                ['gzr',
                    'dashboard',
                    'cat',
                    str(dashboard_response[dashboard]
                        ['content_usage.content_id']),
                    '--host',
                    GZR_INSTANCE_NAME,
                    '--dir',
                    f'{content_type}_backup']
            )
            print(f'''backing up dashboard id {dashboard_response[dashboard]["content_usage.content_id"]}
                        in folder {content_type}_backup''')
            # Comment out the next 2 lines to delete dashboards!
            # print(f'''deleting dashboard id
            #           {dashboard_response[dashboard]["content_usage.content_id"]}''')
            # sdk.delete_dashboard(str(dashboard_response[dashboard]['content_usage.content_id']))
        return delinquent_dashboards

    elif content_type == 'look':
        backupDir('look')
        delinquent_looks = []
        look_response = get_last_accessed_content_dates(
            content_type=content_type,
            delinquent_days=delinquent_days
        )

        for look in range(0, len(look_response)):
            delinquent_looks.append(
                look_response[look]['content_usage.content_id'])
            subprocess.run(
                ['gzr',
                    'look',
                    'cat',
                    str(look_response[look]['content_usage.content_id']),
                    '--host',
                    GZR_INSTANCE_NAME,
                    '--dir',
                    f'{content_type}_backup'])
            print(f'''backing up dashboard id {look_response[look]["content_usage.content_id"]}
                        in folder {content_type}_backup''')

            # Comment out the next 2 lines to delete looks!
            # print(f'deleting look id {look_response[look]["content_usage.content_id"]}')
            # sdk.delete_look(look_response[look]['content_usage.content_id'])
        return delinquent_looks


def delete_content_from_csv(path_to_content: str, delete: bool):
    """iterate through a csv with content expected format title, address

    Args:
        path_to_content (str): [file path to csv file]
        delete (bool): [delete or just see how code is working]

    Returns:
        [type]: [string indicating completion]
    """
    with open(path_to_content, 'r') as csvfile:
        data = []
        csvreader = csv.reader(csvfile)
        next(csvreader)
        data_rows = [row for row in csvreader]
        for element in data_rows:
            content_ids = {}
            content_ids['type'] = element[-1].split('/')[-2]
            content_ids['id'] = element[-1].split('/')[-1]
            data.append(content_ids)

        for content in data:
            if content['type'] == 'dashboards':
                backupDir('dashboard')
                try:
                    print(f'dashboard {content["id"]} would be deleted')
                    subprocess.run(
                        ['gzr',
                            'dashboard',
                            'cat',
                            str(content['id']),
                            '--host',
                            GZR_INSTANCE_NAME,
                            '--dir',
                            'dashboard_backup']
                    )
                    if delete:
                        sdk.delete_dashboard(str(content['id']))
                except error.SDKError:
                    print(f'dashboard {content["id"]} can not be found')
            elif content['type'] == 'looks':
                backupDir('look')
                try:
                    print(f'look {content["id"]} would be deleted')
                    subprocess.run(
                        ['gzr',
                            'look',
                            'cat',
                            str(content['id']),
                            '--host',
                            GZR_INSTANCE_NAME,
                            '--dir',
                            'look_backup']
                    )
                    if delete:
                        sdk.delete_look(content['id'])
                except error.SDKError:
                    print(f'look {content["id"]} can not be found')

        return 'completed deletion processes'


def find_delinquent_content_view_count(delinquent_days: int, view_count: int):
    response = sdk.search_content_views(view_count=view_count)
    delinquent_content = []
    for content in range(0, len(response)):
        try:
            last_used_date = response[content].last_viewed_at
            last_used_date = datetime.datetime.strptime(
                last_used_date[0:10], "%Y-%m-%d")
            days_since_usage = abs(
                datetime.datetime.now() - last_used_date).days
            if days_since_usage < delinquent_days:
                delinquent_content.append(response[content].id)

        except AttributeError:
            print(f'user {response[content].id} did not login through saml')
    return delinquent_content


if __name__ == "__main__":
    ini_file = '/usr/local/google/home/hugoselbie/code_sample/py/projects/ini/looker.ini'

    sdk = looker_sdk.init31(config_file=ini_file)

    # example usage
    print(deliquent_content(content_type='look', delinquent_days=3))
    # print(find_delinquent_content_view_count(90, 1))
    # print(delete_content_from_csv('clients/sunrun/test.csv', delete=False))
