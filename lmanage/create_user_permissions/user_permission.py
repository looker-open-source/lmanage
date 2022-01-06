import logging
import sys
import time
import json
import coloredlogs
from pprint import pprint
import looker_sdk
from looker_sdk import models

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')


def get_role_metadata(
        parsed_yaml: dict) -> list:
    role_permission = []
    del parsed_yaml['role_admin']
    for group_name, group_info in parsed_yaml.items():
        if 'role' in group_name:
            role_name = group_info['role']
            temp = {}
            if 'permissions' in group_info.keys():
                temp['role_name'] = role_name
                temp['permission'] = group_info['permissions']
                temp['model_set_value'] = group_info['model_set']
                temp['teams'] = group_info['team']
                role_permission.append(temp)
            else:
                temp['role_name'] = role_name
                role_permission.append(temp)

    logger.debug(role_permission)
    return role_permission


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
        model_sets = model.get('model_set_value')
        model_set_name = model.get('role_name')
        body = models.WriteModelSet(
            name=model_set_name.lower(), models=model_sets)
        try:
            model = sdk.create_model_set(body=body)
        except looker_sdk.error.SDKError as modelerror:
            logger.info(modelerror.args[0])
            model = sdk.search_model_sets(name=model_set_name)[0]
            model_set_id = model.id
            model = sdk.update_model_set(model_set_id=model_set_id, body=body)
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


def create_roles(
        sdk: looker_sdk,
        all_model_sets: list,
        all_permission_sets: list,
        role_metadata_list: list) -> list:

    model_set_dict = {model.name: model.id for model in all_model_sets}
    permission_set_dict = {perm.name: perm.id for perm in all_permission_sets}

    role_output = []
    for role in role_metadata_list:
        role_name = role.get('role_name')
        permission_set_id = permission_set_dict.get(role_name.lower())
        model_set_id = model_set_dict.get(role_name.lower())
        body = models.WriteRole(
            name=role_name,
            permission_set_id=permission_set_id,
            model_set_id=model_set_id
        )
        try:
            role = sdk.create_role(
                body=body
            )
        except looker_sdk.error.SDKError as roleerror:
            logger.debug(roleerror)
            role_id = sdk.search_roles(name=role_name)[0].id
            role = sdk.update_role(role_id=role_id, body=body)
        temp = {}
        temp['role_id'] = role.id
        temp['role_name'] = role_name
        role_output.append(temp)
    logger.info(role_output)
    return role_output


def sync_roles(
        sdk: looker_sdk,
        all_roles: list,
        role_metadata_list: list):

    all_role_dict = {role.name: role.id for role in all_roles}
    all_role_dict.pop('Admin')
    yaml_role = [role.get('role_name') for role in role_metadata_list]

    for role_name in all_role_dict.keys():
        if role_name not in yaml_role:
            role_id = sdk.search_roles(name=role_name)[0].id
            sdk.delete_role(role_id=role_id)


def set_role(
        role_id: str,
        sdk: looker_sdk,
        group_id: list) -> str:
    try:
        sdk.set_role_groups(role_id, group_id)
        return logger.info(f'attributing {group_id} permissions on instance')
    except looker_sdk.error.SDKError:
        return logger.info('something went wrong')


def attach_role_to_group(
    sdk: looker_sdk,
    role_metadata: list,
        created_role_metadata: list,
        all_roles: list):

    all_groups = sdk.all_groups()
    role_dict = {role.name: role.id for role in all_roles}
    group_dict = {group.name: group.id for group in all_groups}

    for role in role_metadata:
        teams = role.get('teams')
        role_id = role_dict.get(role.get('role_name'))
        group_id_list = []
        for team in teams:
            group_id = group_dict.get(team)
            group_id_list.append(group_id)
        set_role(role_id=role_id, group_id=group_id_list, sdk=sdk)

# def folder_output(
#         sdk: looker_sdk,
#         group_metadata: list,
#         group_config: dict) -> list:
#     response = []
#     for group_name, group_info in group_config.items():
#         folder_info = group_info.get('folder', None)

#         if folder_info:
#             content_metadata_id = sdk.search_folders(
#                 name=folder_info['name'])
#             for group in group_metadata:
#                 folder_provision = {}
#                 folder_provision['name'] = folder_info['name']
#                 folder_provision['cmi'] = content_metadata_id[0].content_metadata_id
#                 # folder_provision['folder_id'] = folder_info['folder_id']
#                 if folder_info['team_edit'] in group.values():
#                     folder_provision['group_id'] = group['group_id']
#                     folder_provision['content_metadata_id'] = group['content_metadata_id']

#                     folder_provision['team_info'] = {}
#                     folder_provision['team_info']['folder_id'] = group['folder_id']
#                     folder_provision['team_info']['group_id'] = group['group_id']
#                     folder_provision['team_info']['group_name'] = group['group_name']
#                     folder_provision['team_info']['permission'] = 'edit'
#                     response.append(folder_provision)
#                 else:
#                     for team in folder_info['team_view']:
#                         if team in group.values():
#                             folder_provision['team_info'] = {}
#                             folder_provision['group_id'] = group['group_id']
#                             # folder_provision['content_metadata_id'] = group['content_metadata_id']
#                             folder_provision['content_metadata_id'] = group['content_metadata_id']
#                             folder_provision['team_info']['folder_id'] = group['folder_id']
#                             folder_provision['team_info']['group_id'] = group['group_id']
#                             folder_provision['team_info']['group_name'] = group['group_name']
#                             folder_provision['team_info']['permission'] = 'view'
#                             response.append(folder_provision)

#     return response


# def ancestor_folder_change():
#     ancestors = sdk.folder_ancestors(folder_id=folder_id)
#     pass


# def provision_folders_with_group_access(
#         sdk: looker_sdk,
#         folder_permission_metadata: list) -> str:

#     for access_item in folder_permission_metadata:

#         content_metadata_id = access_item["cmi"]

#         # check for existing access to the folder
#         content_metadata_accesses = {
#             access.group_id: access
#             for access in sdk.all_content_metadata_accesses(
#                 content_metadata_id=content_metadata_id)}

#         group_id = access_item['team_info']['group_id']
#         permission = access_item['team_info']['permission']
#         if group_id in content_metadata_accesses.keys():
#             current_access = content_metadata_accesses.get(group_id)

#             if current_access.permission_type.value == permission:
#                 logger.info(
#                     f'--> Group {group_id} already has access, no changes made.')

#             else:
#                 # don't want to inherit access from parent folders
#                 sdk.update_content_metadata(
#                     content_metadata_id=content_metadata_id,
#                     body={'inherits': False}
#                 )
#                 sdk.update_content_metadata_access(
#                     content_metadata_access_id=current_access.id,
#                     body=models.ContentMetaGroupUser(
#                         content_metadata_id=content_metadata_id,
#                         permission_type=permission,
#                         group_id=group_id
#                     ))

#                 logging.info(
#                     f'--> Changed permission type to {permission}.')

#         # no existing access
#         # create from scratch
#         else:
#             # don't want to inherit access from parent folders
#             sdk.update_content_metadata(
#                 content_metadata_id=content_metadata_id,
#                 body={'inherits': False}
#             )

#             sdk.create_content_metadata_access(
#                 body=models.ContentMetaGroupUser(
#                     content_metadata_id=content_metadata_id,
#                     permission_type=permission,
#                     group_id=group_id
#                 )
#             )
#             logger.info(
#                 f'--> Sucessfully permissioned group {group_id} {permission} access.')


# def remove_all_user_group(
#         sdk: looker_sdk,
#         folder_permission_metadata: list):

#     # remove parent Shared group instance access
#     try:
#         sdk.update_content_metadata_access(
#             content_metadata_access_id=1,
#             body=models.ContentMetaGroupUser(
#                 permission_type='view',
#                 content_metadata_id=1,
#                 group_id=1
#             )
#         )
#     except looker_sdk.error.SDKError:
#         logger.info('All Users group already configured')
#     clean = list()
#     for avt in folder_permission_metadata:
#         temp = {}
#         temp['name'] = avt['name']
#         temp['cmi'] = avt['cmi']
#         clean.append(temp)
#     res_list = [i for n, i in enumerate(clean) if i not in clean[n + 1:]]

#     for access_item in res_list:
#         time.sleep(1)

#         content_metadata_id = access_item["cmi"]

#         # check for existing access to the folder
#         content_metadata_accesses = {
#             access.group_id: access
#             for access in sdk.all_content_metadata_accesses(
#                 content_metadata_id=content_metadata_id)}

#         for id, value in content_metadata_accesses.items():
#             logger.debug(f'Checking item {value.id}')
#             if value.group_id == 1:
#                 cmaid = value['id']
#                 sdk.delete_content_metadata_access(
#                     content_metadata_access_id=cmaid)
#                 break


def main(**kwargs):
    """ Sync Looker group membership, group attributes, roles, and content access

     This method creates groups with the specified membership and user attributes,
     assigns the groups to the specified roles, and permissions access to the
     specified folders. Note that each group only has one of (1) role, (2) attributes
     and (3) folder access.

     :param dict group_config: Mapping from Looker group name to group metadata.
     :param dict ldap_membership: Mapping from an LDAP group name to a list of member LDAPs.
     :rtype: None
     """
    div = '--------------------------------------'

    ini_file = kwargs.get("ini_file")
    yaml_path = kwargs.get("yaml_path")
    logger.info(div)
    logger.info('parsing yaml file')
    group_config = read_provision_yaml(yaml_path)
    sdk = looker_sdk.init31(config_file=ini_file)

    group_metadata = search_group_id(sdk, group_config)

    # collect content access information
    logger.info(div)
    logger.info('Collecting content access information...')
    folder_permission_metadata = folder_output(sdk=sdk,
                                               group_metadata=group_metadata, group_config=group_config)

    # update content access
    logger.info(div)
    logger.info('Adding content access...')
    provision_folders_with_group_access(
        sdk, folder_permission_metadata=folder_permission_metadata)

    # create roles
    logger.info(div)
    logging.info('Creating Roles')
    role_metadata = create_role_mapping(group_config=group_config)
    role_create = create_roles(sdk=sdk, role_mapping=role_metadata)
    attach_role_to_group(sdk=sdk, role_metadata=role_create,
                         group_config=group_config)

    # removing all user group from folders
    logger.info(div)
    logger.info('Removing all user group from folders')
    remove_all_user_group(
        sdk=sdk, folder_permission_metadata=folder_permission_metadata)


if __name__ == "__main__":
    main(
        ini_file='/usr/local/google/home/hugoselbie/code_sample/py/ini/k8.ini',
        yaml_path='/usr/local/google/home/hugoselbie/code_sample/py/clients/snap/okta_groups/snap_group_mapping.yaml')
