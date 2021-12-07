import logging
import sys
import time
import json
import coloredlogs
from pprint import pprint
import looker_sdk
from looker_sdk import models

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


def create_role_mapping(
        group_config: list) -> list:
    role_permission = []
    del group_config['role_admin']
    for group_name, group_info in group_config.items():
        if 'role' in group_name.split('_'):
            temp = {}
            temp['role_name'] = group_name.lower()
            temp['permission'] = group_info['role']
            model_set_name = group_info.get('team')[0]
            temp['model_set_std'] = f'{model_set_name}_std_sql'.lower()
            temp['model_set_legacy'] = f'{model_set_name}_legacy_sql'.lower(
            )
            role_permission.append(temp)
    return role_permission


def create_roles(
        sdk: looker_sdk,
        role_mapping: list) -> list:
    role_dict = {role.id: role.name for role in sdk.all_roles()}
    role_output = []
    for role in role_mapping:
        role_name = role['role_name']
        if role_name in role_dict.values():
            logger.info(f'--> Role {role_name} has already been configured.')
            role_output.append(sdk.search_roles(name=role_name))
        else:
            legacy_model = role['model_set_legacy']
            standard_model = role['model_set_std']
            permission_metadata = sdk.search_permission_sets(
                name=role['permission'])
            permission_id = permission_metadata[0].id
            try:
                model_set_provision = sdk.create_model_set(
                    body=(models.WriteModelSet(
                        models=[legacy_model, standard_model],
                        name=f'{role_name}_model_set'
                    ))
                )
                model_id = model_set_provision['id']
            except looker_sdk.error.SDKError:
                logger.info('model set already exists')
                model_set_provision = sdk.search_model_sets(
                    name=f'{role_name}_model_set')
                model_id = model_set_provision[0]['id']

            logger.info(f'--> Trying to create role {role_name}')
            role_metadata = sdk.create_role(
                body=models.WriteRole(
                    name=role['role_name'],
                    permission_set_id=permission_id,
                    model_set_id=model_id
                )
            )
            role_output.append(role_metadata)
            logger.info(f'--> Role {role_name} being created on your system.')
    return role_output


def set_role(
        role_id: str,
        sdk: looker_sdk,
        group_id: str) -> str:
    try:
        sdk.set_role_groups(role_id, [group_id])
        return logger.info(f'attributing {group_id} permissions on instance')
    except looker_sdk.error.SDKError:
        return logger.info('something went wrong')


def attach_role_to_group(
        sdk: looker_sdk,
        role_metadata: list,
        group_config: list) -> list:

    all_groups = sdk.all_groups()
    all_roles = sdk.all_roles()
    role_dict = {role.name: role.id for role in all_roles}
    group_dict = {group.name: group.id for group in all_groups}
    for group_name, group_info in group_config.items():
        if group_name in group_dict.keys():
            role_id = role_dict.get(group_name.lower())

            if 'team' in group_info.keys():
                for team in group_info['team']:
                    group_id = group_dict.get(team)
                    set_role(role_id=role_id, group_id=group_id, sdk=sdk)
            else:
                group_id = group_dict.get(group_name)
                set_role(role_id=role_id, group_id=group_id, sdk=sdk)


def folder_output(
        sdk: looker_sdk,
        group_metadata: list,
        group_config: dict) -> list:
    response = []
    for group_name, group_info in group_config.items():
        folder_info = group_info.get('folder', None)

        if folder_info:
            content_metadata_id = sdk.search_folders(
                name=folder_info['name'])
            for group in group_metadata:
                folder_provision = {}
                folder_provision['name'] = folder_info['name']
                folder_provision['cmi'] = content_metadata_id[0].content_metadata_id
                # folder_provision['folder_id'] = folder_info['folder_id']
                if folder_info['team_edit'] in group.values():
                    folder_provision['group_id'] = group['group_id']
                    folder_provision['content_metadata_id'] = group['content_metadata_id']

                    folder_provision['team_info'] = {}
                    folder_provision['team_info']['folder_id'] = group['folder_id']
                    folder_provision['team_info']['group_id'] = group['group_id']
                    folder_provision['team_info']['group_name'] = group['group_name']
                    folder_provision['team_info']['permission'] = 'edit'
                    response.append(folder_provision)
                else:
                    for team in folder_info['team_view']:
                        if team in group.values():
                            folder_provision['team_info'] = {}
                            folder_provision['group_id'] = group['group_id']
                            # folder_provision['content_metadata_id'] = group['content_metadata_id']
                            folder_provision['content_metadata_id'] = group['content_metadata_id']
                            folder_provision['team_info']['folder_id'] = group['folder_id']
                            folder_provision['team_info']['group_id'] = group['group_id']
                            folder_provision['team_info']['group_name'] = group['group_name']
                            folder_provision['team_info']['permission'] = 'view'
                            response.append(folder_provision)

    return response


def ancestor_folder_change():
    ancestors = sdk.folder_ancestors(folder_id=folder_id)
    pass


def provision_folders_with_group_access(
        sdk: looker_sdk,
        folder_permission_metadata: list) -> str:

    for access_item in folder_permission_metadata:

        content_metadata_id = access_item["cmi"]

        # check for existing access to the folder
        content_metadata_accesses = {
            access.group_id: access
            for access in sdk.all_content_metadata_accesses(
                content_metadata_id=content_metadata_id)}

        group_id = access_item['team_info']['group_id']
        permission = access_item['team_info']['permission']
        if group_id in content_metadata_accesses.keys():
            current_access = content_metadata_accesses.get(group_id)

            if current_access.permission_type.value == permission:
                logger.info(
                    f'--> Group {group_id} already has access, no changes made.')

            else:
                # don't want to inherit access from parent folders
                sdk.update_content_metadata(
                    content_metadata_id=content_metadata_id,
                    body={'inherits': False}
                )
                sdk.update_content_metadata_access(
                    content_metadata_access_id=current_access.id,
                    body=models.ContentMetaGroupUser(
                        content_metadata_id=content_metadata_id,
                        permission_type=permission,
                        group_id=group_id
                    ))

                logging.info(
                    f'--> Changed permission type to {permission}.')

        # no existing access
        # create from scratch
        else:
            # don't want to inherit access from parent folders
            sdk.update_content_metadata(
                content_metadata_id=content_metadata_id,
                body={'inherits': False}
            )

            sdk.create_content_metadata_access(
                body=models.ContentMetaGroupUser(
                    content_metadata_id=content_metadata_id,
                    permission_type=permission,
                    group_id=group_id
                )
            )
            logger.info(
                f'--> Sucessfully permissioned group {group_id} {permission} access.')


def remove_all_user_group(
        sdk: looker_sdk,
        folder_permission_metadata: list):

    # remove parent Shared group instance access
    try:
        sdk.update_content_metadata_access(
            content_metadata_access_id=1,
            body=models.ContentMetaGroupUser(
                permission_type='view',
                content_metadata_id=1,
                group_id=1
            )
        )
    except looker_sdk.error.SDKError:
        logger.info('All Users group already configured')
    clean = list()
    for avt in folder_permission_metadata:
        temp = {}
        temp['name'] = avt['name']
        temp['cmi'] = avt['cmi']
        clean.append(temp)
    res_list = [i for n, i in enumerate(clean) if i not in clean[n + 1:]]

    for access_item in res_list:
        time.sleep(1)

        content_metadata_id = access_item["cmi"]

        # check for existing access to the folder
        content_metadata_accesses = {
            access.group_id: access
            for access in sdk.all_content_metadata_accesses(
                content_metadata_id=content_metadata_id)}

        for id, value in content_metadata_accesses.items():
            logger.debug(f'Checking item {value.id}')
            if value.group_id == 1:
                cmaid = value['id']
                sdk.delete_content_metadata_access(
                    content_metadata_access_id=cmaid)
                break


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
