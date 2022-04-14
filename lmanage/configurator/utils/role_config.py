from looker_sdk import models
import looker_sdk
import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')

'''
Read in the permission metadata

create if not exists permission set

create if not exists model set

sync permissions
sync model sets
'''


def get_role_creation_metadata(
        metadata_type: str,
        parsed_yaml: dict) -> list:
    '''
    Read in metadata from either permission or role 
    '''
    role_metadata = []
    for group_name, group_info in parsed_yaml.items():
        if metadata_type in group_name:
            for mtype, mval in group_info.items():
                role_name = mtype
                temp = {}
                temp['role_name'] = role_name
                temp['permission'] = mval.get('permissions')
                role_metadata.append(temp)

    logger.debug(role_metadata)
    print(role_metadata)
    return role_metadata


def sync_permission_set(
        sdk: looker_sdk,
        all_permission_sets: list,
        permission_set_list: list):

    permissions_dict = {p.name: p.id for p in all_permission_sets}
    permissions_dict.pop('Admin')
    yaml_permissions = [role.get('name') for role in permission_set_list]

    for permission_set_name in permissions_dict.keys():

        if permission_set_name not in yaml_permissions:
            permission_id = sdk.search_permission_sets(
                name=permission_set_name)[0].id
            sdk.delete_permission_set(permission_set_id=permission_id)


def create_permission_set(
        sdk: looker_sdk,
        permission_set_list: list):

    final_response = []
    for permission in permission_set_list:
        permission_set_name = permission.get('role_name')
        permissions = permission.get('permission')
        body = models.WritePermissionSet(
            name=permission_set_name.lower(),
            permissions=permissions
        )
        try:
            perm = sdk.create_permission_set(
                body=body
            )
        except looker_sdk.error.SDKError:
            perm = sdk.search_permission_sets(name=permission_set_name)[0]
            pid = perm.id
            perm = sdk.update_permission_set(permission_set_id=pid, body=body)

        temp = {}
        temp['name'] = perm.name
        temp['pid'] = perm.id
        final_response.append(temp)

    logger.debug(final_response)
    return final_response


def create_model_set(
        sdk: looker_sdk,
        model_set_list: list) -> list:

    final_response = []
    for model in model_set_list:
        model_set_metadata = model.get('model_set_value')
        for model_set in model_set_metadata:
            model_set_name = model_set.get('name')
            attributed_models = model_set.get('models')
            body = models.WriteModelSet(
                name=model_set_name.lower(), models=attributed_models)
            try:
                model = sdk.create_model_set(body=body)
            except looker_sdk.error.SDKError as modelerror:
                logger.info(modelerror.args[0])
                model = sdk.search_model_sets(name=model_set_name)[0]
                model_set_id = model.id
                model = sdk.update_model_set(
                    model_set_id=model_set_id, body=body)
            temp = {}
            temp['model_set_name'] = model.name
            temp['model_set_id'] = model.id
            final_response.append(temp)
    logger.info(final_response)
    return final_response


def sync_model_set(
        sdk: looker_sdk,
        all_model_sets: list,
        model_set_list: list):

    model_sets_dict = {p.name: p.id for p in all_model_sets}
    model_sets_dict.pop('All')
    yaml_model = [role.get('model_set_name') for role in model_set_list]

    for model_set_name in model_sets_dict.keys():

        if model_set_name not in yaml_model:
            model_id = sdk.search_model_sets(
                name=model_set_name)[0].id
            sdk.delete_model_set(model_set_id=model_id)
