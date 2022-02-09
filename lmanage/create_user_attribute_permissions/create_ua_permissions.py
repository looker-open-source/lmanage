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


def existing_user_attributes(
        sdk: looker_sdk) -> dict:
    all_instance_ua = sdk.all_user_attributes()

    all_ua = {ua.name: ua.id for ua in all_instance_ua}
    return all_ua


def create_user_attribute_if_not_exists(
        sdk: looker_sdk,
        ua_metadata: list):
    existing_ua = existing_user_attributes(
        sdk=sdk)

    for ua in ua_metadata:
        name = ua['name']
        if name in existing_ua:
            logger.info(
                f'user attribute {name} already exists on this instance')
        else:
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
            logger.info(f'created user attribute {response.label}')


def sync_user_attributes(sdk: looker_sdk,
                         ua_metadata: list) -> None:
    instance_ua = existing_user_attributes(sdk=sdk)
    config_ua = [ua['name'] for ua in ua_metadata]
    sys_default_ua = [
        'email',
        'first_name',
        'id',
        'landing_page',
        'last_name',
        'locale',
        'name'
    ]

    for ua in sys_default_ua:
        if ua in instance_ua:
            instance_ua.pop(ua, None)

    for ua_name in instance_ua:
        if ua_name not in config_ua:
            ua_id = instance_ua.get(ua_name)
            sdk.delete_user_attribute(ua_id)
            logger.info(
                f'deleting ua {ua_name} because it is not listed in the yaml config')


def add_group_values_to_ua(sdk: looker_sdk,
                           ua_metadata: list) -> None:

    instance_ua = existing_user_attributes(sdk=sdk)
    all_instance_groups = sdk.all_groups()
    group_metadata = {group.name: group.id for group in all_instance_groups}
    for ua in ua_metadata:
        meta_value = ','.join(ua['value'])
        for group in ua['team']:
            try:
                group_id = group_metadata.get(group)
            except looker_sdk.error.SDKError:
                logger.info('group dont exist mofo')
        ua_id = instance_ua.get(ua['name'])

        params_to_add = models.UserAttributeGroupValue(
            value=meta_value,
            value_is_hidden=False
        )

        sdk.update_user_attribute_group_value(
            group_id=group_id,
            user_attribute_id=ua_id,
            body=params_to_add)
