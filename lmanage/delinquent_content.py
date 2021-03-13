from looker_sdk import models, error
import looker_sdk
import configparser
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


def read_ini(ini="../looker.ini"):
    config = configparser.ConfigParser()
    config.read(ini)

    return config


def get_gzr_creds(ini, env='Looker'):
    ini = read_ini(ini)
    env_record = ini[env]
    host, port = env_record["base_url"].replace("https://", "").split(":")
    client_id = env_record["client_id"]
    client_secret = env_record["client_secret"]
    verify_ssl = env_record["verify_ssl"]

    return (host, port, client_id, client_secret, verify_ssl)


def backUpContent(content_details, ini, backuploc, env='Looker'):
    host, port, client_id, client_secret, verify_ssl = get_gzr_creds(ini, env)
    logger.wtf(content_details)
    gzr_command = [
        "gzr",
        f"{content_details['content_usage.content_type']}",
        "cat",
        f"{content_details['content_usage.content_id']}",
        "--dir",
        backuploc,
        "--host",
        host,
        "--port",
        port,
        "--client-id",
        client_id,
        "--client-secret",
        client_secret
    ]
    subprocess.run(gzr_command)


def delinquent_content(content_export, ini, backuploc):
    """identify content with delinquent days of x. passed into api call for run inline query
    this input is then used to both delete the content and use gzr to export the json
    content rendering for easy restoration after delete
    """
    for content in content_export:
        logger.wtf(content)
        backUpContent(content, ini, backuploc='./test/')

    # response = pd.DataFrame(content_export)
    # # looks.to_csv('./delinquentcontent.csv')
    # logger.success(response.head(15))
    # return response.head(15)


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


def main(**kwargs):
    ini_file = kwargs.get("ini_file")
    delinquent_day = kwargs.get("days")
    backup_location = kwargs.get("backupLocation")

    sdk = looker_sdk.init31(
        config_file=ini_file)

    backupLocation = backup_location if len(
        backup_location) > 0 else backupDir('looker_backup_content')
    delinquent_looks = get_last_accessed_content_dates(
        content_type='look', delinquent_days=delinquent_day, sdk=sdk)
    logger.wtf(delinquent_looks)
    delinquent_dashboards = get_last_accessed_content_dates(
        content_type='dashboard', delinquent_days=delinquent_day, sdk=sdk)
    logger.wtf(delinquent_dashboards)

    delinquent_content(content_export=delinquent_looks,
                       ini=ini_file, backuploc=backupLocation)
    delinquent_content(content_export=delinquent_dashboards,
                       ini=ini_file, backuploc=backupLocation)


if __name__ == "__main__":
    main(ini_file='/usr/local/google/home/hugoselbie/code_sample/py/projects/ini/looker.ini',
         days=2, backupLocation='./test/')
