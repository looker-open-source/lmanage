from looker_sdk import models, error
import looker_sdk
import configparser as ConfigParser
import pandas as pd
import json
import csv
import os
import subprocess
import datetime
from coloredlogger import ColoredLogger
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
logger = ColoredLogger()


def backupDir(content_type: str):
    """function to generate backup directories

    Args:
        content_type (str): dashboard/look switch
    """
    path = content_type

    if not os.path.exists(path):
        os.mkdir(path)
        print(f"Successfully created the directory {path}")
    elif not os.path.isdir(path):
        print(f"Creation of the directory {path} has failed")


def get_last_accessed_content_dates(content_type: str, delinquent_days: int, sdk):
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
    logger.wtf(query_response)
    query_response = json.loads(query_response)

    return query_response


def delinquent_content(days: int, sdk, backuploc: str):
    """identify content with delinquent days of x. passed into api call for run inline query
    this input is then used to both delete the content and use gzr to export the json
    content rendering for easy restoration after delete
    """
    backupDir('looker_backup_content')
    content_types = ['look', 'dashboard']
    for content in content_types:
        delinquent_content = []
        content_response = get_last_accessed_content_dates(
            content_type=content, delinquent_days=days, sdk=sdk)
        logger.wtf(content_response)
        for content_type in range(0, len(content_response)):
            if content == 'Look':
                delinquent_content.append(
                    content_response[content_type]['content_usage.content_id'])
                logger.wtf(delinquent_content)
                subprocess.run(
                    ['gzr',
                     content_types,
                     'cat',
                     content_response[content_type]['content_usage.content_id'],
                     '--host',
                     backuploc,
                     '--dir',
                     'looker_backup_content'])
                logger.success(
                    f'''backing up content id {content_response[content_type]['content_usage.content_id']} in folder ''')
    looks = pd.DataFrame(get_last_accessed_content_dates(
        content_type=content, delinquent_days=days, sdk=sdk))
    looks.to_csv('./delinquentcontent.csv')
    logger.success(looks.head(15))


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


def find_delinquent_content_view_count(delinquent_days: int, view_count: int, sdk):
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


def main(**kwargs):
    ini_file = kwargs.get("ini_file")
    delinquent_day = kwargs.get("days")
    backup_location = kwargs.get("backup_url")

    sdk = looker_sdk.init31(
        config_file=ini_file)

    delinquent_content(days=delinquent_day, sdk=sdk, backuploc=backup_location)


if __name__ == "__main__":
    main(ini_file='/usr/local/google/home/hugoselbie/code_sample/py/projects/ini/looker.ini',
         days=2, content_type='Look', backup_url='profservices.dev.looker.com')
