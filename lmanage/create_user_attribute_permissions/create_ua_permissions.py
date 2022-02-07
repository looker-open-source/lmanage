import logging
import time
import coloredlogs
from looker_sdk import models
import looker_sdk

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


def get_user_attribute_metadata(
        sdk: looker_sdk,
        parsed_yaml: dict) -> list:
    response = []
    for k, v in parsed_yaml.items():
        if 'ua' in k:
            response.append(v)
    return response


def sync_user_attributes(
        sdk: looker_sdk,
        ua_metadata: list):
    all_instance_ua = sdk.all_user_attributes()
    all_ua = {ua['name']: ua['id'] for ua in all_instance_ua}


def create_user_attribute(
        sdk: looker_sdk,
        ua_metadata: list):
    for ua in ua_metadata:
        name = ua['name']
        datatype = ua['type']
        value_is_hidden = ua['hidden_value']
        user_view = ua['user_view']
        user_edit = ua['user_edit']

        ua_permissions = models.WriteUserAttribute(
            name=name,
            label=name,
            type=datatype,
            value_is_hidden=value_is_hidden,
            user_can_view=user_view,
            user_can_edit=user_edit
        )

        response = sdk.create_user_attribute(body=ua_permissions)
        print(response)

    # ua_permissions = models.WriteUserAttribute(
    #     name='foo',
    #     type='string',
    #     value_is_hidden=false,
    #     user_can_view=true,
    #     user_can_edit=false)
    # pass
