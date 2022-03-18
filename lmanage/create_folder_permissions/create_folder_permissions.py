import logging
import time
import coloredlogs
from looker_sdk import models
import looker_sdk

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


def get_content_access_metadata(
        sdk: looker_sdk,
        instance_folder_metadata: list) -> list:
    response = []

    for folder in instance_folder_metadata:
        temp_dict = {}
        temp_dict['name'] = folder.get('name')
        temp_dict['cmi'] = folder.get('content_metadata_id')
        edit_group = folder.get('team_edit')
        view_group = folder.get('team_view')

        perms = []
        if isinstance(edit_group, list):
            for group in edit_group:
                group_dict = {}
                egmetadata = sdk.search_groups(name=group)
                group_dict['name'] = group
                group_dict['id'] = egmetadata[0].id
                group_dict['permission'] = 'edit'
                perms.append(group_dict)
        else:
            group_dict = {}
            group_dict['name'] = 'no_name'
            group_dict['id'] = 'no_id'
            group_dict['permission'] = 'no_permission'
            perms.append(group_dict)

        if isinstance(view_group, list):
            for group in view_group:
                group_dict = {}
                vgmetadata = sdk.search_groups(name=group)
                group_dict['name'] = group
                group_dict['id'] = vgmetadata[0].id
                group_dict['permission'] = 'view'
                perms.append(group_dict)
        else:
            group_dict = {}
            group_dict['name'] = 'no_name'
            group_dict['id'] = 'no_id'
            group_dict['permission'] = 'no_permission'
            perms.append(group_dict)

        temp_dict['group_permissions'] = perms
        response.append(temp_dict)
    return response


def remove_content_access(
        sdk: looker_sdk,
        cm_accesses: dict,
        yaml_group_ids: list):

    # loop through the accesses and if id is not in true group delete it
    for group_id in cm_accesses.keys():
        if group_id not in yaml_group_ids:
            delete_cmi = cm_accesses.get(group_id).id
            sdk.delete_content_metadata_access(
                content_metadata_access_id=delete_cmi)
            logger.info(f'deleting access for group {group_id}')
        elif 'no_id' in yaml_group_ids:
            pass


def create_content_metadata_access(
        sdk: looker_sdk,
        group_id: int,
        permission_input: str,
        content_metadata_id: int) -> dict:

    sdk.create_content_metadata_access(
        body=models.ContentMetaGroupUser(
            content_metadata_id=content_metadata_id,
            permission_type=permission_input,
            group_id=group_id
        )
    )
    logger.info(
        f'''--> Sucessfully permissioned group
                {group_id} {permission_input} access.''')


def check_folder_ancestors(
        sdk: looker_sdk,
        group_id: int,
        cmaid: int):

    folder_id = sdk.content_metadata(content_metadata_id=cmaid).folder_id
    ancestors_list = sdk.folder_ancestors(folder_id=folder_id)

    for ancestor in ancestors_list:
        ancestor_cmaid = ancestor.content_metadata_id
        folder_access = check_existing_access(
            sdk=sdk,
            content_metadata_id=ancestor_cmaid)
        if group_id not in folder_access:
            if check_folder_inheritance(sdk=sdk, content_metadata_id=ancestor_cmaid):
                update_folder_inheritance(
                    sdk=sdk, cmaid=ancestor_cmaid, inheritance=False)

                create_content_metadata_access(
                    sdk=sdk,
                    group_id=group_id,
                    permission_input='view',
                    content_metadata_id=ancestor_cmaid)
                update_folder_inheritance(
                    sdk=sdk, cmaid=ancestor_cmaid, inheritance=True)
            else:
                create_content_metadata_access(
                    sdk=sdk,
                    group_id=group_id,
                    permission_input='view',
                    content_metadata_id=ancestor_cmaid)


def check_folder_inheritance(
        sdk: looker_sdk,
        content_metadata_id: int) -> bool:
    response = sdk.content_metadata(content_metadata_id=content_metadata_id)
    r = response.inherits
    return r


def update_folder_inheritance(
        sdk: looker_sdk,
        cmaid: int,
        inheritance: bool):

    # don't want to inherit access from parent folders
    sdk.update_content_metadata(
        content_metadata_id=cmaid,
        body=models.WriteContentMeta(inherits=inheritance)
    )


def add_content_access(
        sdk: looker_sdk,
        cm_accesses: dict,
        cmaid: int,
        group_permissions: list) -> dict:

    for group in group_permissions:
        group_id = group.get('id')
        permission = group.get('permission')
        if permission == 'no_permission':

            check_folder_ancestors(
                sdk=sdk,
                group_id=group_id,
                cmaid=cmaid)
            update_folder_inheritance(
                sdk=sdk,
                cmaid=cmaid,
                inheritance=True
            )
        else:
            check_folder_ancestors(
                sdk=sdk,
                group_id=group_id,
                cmaid=cmaid
            )
            update_folder_inheritance(
                sdk=sdk,
                cmaid=cmaid,
                inheritance=False
            )

        if group_id in cm_accesses.keys():
            current_access = cm_accesses.get(group_id)

            if current_access.permission_type == permission:
                logger.info(
                    f'''--> Group {group_id} already has access,
                    no changes made.''')

            else:
                try:
                    sdk.update_content_metadata_access(
                        content_metadata_access_id=current_access.id,
                        body=models.ContentMetaGroupUser(
                            content_metadata_id=cmaid,
                            permission_type=permission,
                            group_id=group_id
                        ))
                except looker_sdk.error.SDKError as foldererror:
                    logger.debug(foldererror.args[0])

                logging.info(
                    f'--> Changed permission type to {permission}.')

        # no existing access
        # create from scratch
        elif permission == 'no_permission':
            pass
        else:
            create_content_metadata_access(
                sdk=sdk,
                content_metadata_id=cmaid,
                permission_input=permission,
                group_id=group_id
            )


def check_existing_access(
        sdk: looker_sdk,
        content_metadata_id: int) -> dict:
    # check for existing access to the folder
    response = {
        access.group_id: access
        for access in sdk.all_content_metadata_accesses(
            content_metadata_id=content_metadata_id)}
    return response


def provision_folders_with_group_access(
        sdk: looker_sdk,
        content_access_metadata_list: list) -> str:

    for access_item in content_access_metadata_list:
        content_metadata_id = access_item["cmi"]
        # check for existing access to the folder
        content_metadata_accesses = check_existing_access(
            sdk=sdk, content_metadata_id=content_metadata_id)

        # sync content_metadata back to yaml file
        # make sure the group_id's are in the yaml file
        true_group_id = [
            access_item['group_permissions'][elem]['id']
            for elem in range(0, len(access_item['group_permissions']))]

        try:
            remove_content_access(
                sdk=sdk,
                cm_accesses=content_metadata_accesses,
                yaml_group_ids=true_group_id)
        except looker_sdk.error.SDKError as error:
            raise Exception(
                f'You have an inheritance error in your YAML file, please verify that your group can be removed {error}') from error

        gp_permissions = access_item.get('group_permissions')
        if gp_permissions[0].get('id') == 'no_id':
            pass
        else:
            add_content_access(
                sdk=sdk,
                cm_accesses=content_metadata_accesses,
                cmaid=content_metadata_id,
                group_permissions=gp_permissions)


def remove_all_user_group(
        sdk: looker_sdk,
        content_access_metadata_list: list):

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
    for avt in content_access_metadata_list:
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
                cmaid = value.id
                sdk.delete_content_metadata_access(
                    content_metadata_access_id=cmaid)
