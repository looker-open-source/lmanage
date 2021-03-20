from coloredlogger import ColoredLogger
import pandas as pd
import json
from pathlib import Path
import datetime
import configparser as ConfigParser
from looker_sdk import models
import looker_sdk
from os import name
import pandas as pd
import warnings
import lmanage.utils.create_df as create_df

warnings.simplefilter(action='ignore', category=FutureWarning)
logger = ColoredLogger()


def get_user_list(sdk):
    logger.success('Querying System Activity Model')
    query_config = models.WriteQuery(
        model="system__activity",
        view="user",
        fields=[
            "user.id",
            "user.name",
            "user.created_date",
            "user_facts.last_ui_login_date",
            "history.most_recent_query_date",
            "user_facts.last_ui_login_credential_type"],
        filters={
            "user.is_disabled": "No",
            "user_facts.is_looker_employee": "No",
        },
        dynamic_fields="[{\"table_calculation\":\"no_query_login\",\"label\":\"No-Query Login?\",\"expression\":\"${history.most_recent_query_date} < ${user_facts.last_ui_login_date}\",\"value_format\":null,\"value_format_name\":null,\"_kind_hint\":\"measure\",\"_type_hint\":\"yesno\"},{\"table_calculation\":\"days_since_last_login\",\"label\":\"Days Since Last Login\",\"expression\":\"diff_days(${user_facts.last_ui_login_date}, trunc_days(now()))\",\"value_format\":null,\"value_format_name\":null,\"_kind_hint\":\"dimension\",\"_type_hint\":\"number\"}]",
        limit=' 5000'
    )
    query_response = sdk.run_inline_query(
        result_format='json',
        body=query_config
    )
    logger.success('Turning Response into JSON')
    query_response = json.loads(query_response)
    return query_response


def find_delinquent_users(sdk, delinquent_days: int, export_csv=False):
    user_list = get_user_list(sdk=sdk)
    responsedf = create_df.create_df(user_list)

    responsedf = responsedf.replace('NULL', 0)
    logger.wtf(responsedf['days_since_last_login'] == 'NULL')
    responsedf['delinquent'] = responsedf['days_since_last_login'] > delinquent_days
    responsedf.columns = responsedf.columns.str.replace('.', '_', regex=True)
    logger.success('Tabulating data into DataFrame')

    logger.success(responsedf)
    if export_csv:
        responsedf.to_csv()
    disabled_user_list = (responsedf['delinquent'] == True)
    disabled_user_list = responsedf[disabled_user_list]
    iterate = disabled_user_list['user_id'].to_list()
    for user_id in iterate:
        logger.success(
            f'user {user_id} will be disabled if you add the flag --removeuser True')
    return disabled_user_list['user_id'].to_list()


def disable_deliquent_users(user_list: list, sdk):
    """Expects a list of user id's and iterates
    through that list

    Args:
        user_list (list): [a list of looker user ids]

    Returns:
        [list]: [ids of disabled users]
    """
    user_disable_list = []
    for user_id in user_list:
        user_info_body = sdk.user(user_id)
        user_info_body.is_disabled = True
        logger.wtf(user_info_body)
        logger.success(f'user {user_id} has been disabled')
        user_disable_list.append(user_info_body.id)

    return user_disable_list


def main(**kwargs):
    cwd = Path.cwd()
    ini_file = kwargs.get("ini_file")
    days_delinquent = int(kwargs.get("days"))
    rm_user = kwargs.get("removeuser")
    if ini_file:
        parsed_ini_file = cwd.joinpath(ini_file)
    else:
        parsed_ini_file = None
    sdk = looker_sdk.init31(config_file=parsed_ini_file)
    if rm_user:
        response = find_delinquent_users(
            delinquent_days=days_delinquent, sdk=sdk)
        logger.info(response)
        disable_deliquent_users(user_list=response, sdk=sdk)
        return response
    else:
        logger.info(find_delinquent_users(
            delinquent_days=days_delinquent, sdk=sdk))


if __name__ == "__main__":
    main(
        ini_file='../ini/looker.ini',
        days=2,
        removeuser=True
    )
