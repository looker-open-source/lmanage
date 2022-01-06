import logging
import time
import coloredlogs
from looker_sdk import models
import looker_sdk

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


def get_content_access_metadata(
        sdk: looker_sdk,
        parsed_yaml: dict) -> list:
    response = []
    for folder_name, folder_info in parsed_yaml.items():
        folder_provision = {}
        if 'folder' in folder_name:
            fname = folder_info['folder']['name']
            fmetadata = sdk.search_folders(name=fname)
            folder_provision['cmi'] = fmetadata[0].content_metadata_id
            folder_provision['name'] = fname

            edit_group = folder_info['folder']['team_edit']
            view_group = folder_info['folder']['team_view']
            temp = []
            for group in edit_group:
                temp_dict = {}
                egmetadata = sdk.search_groups(name=group)
                temp_dict['name'] = group
                temp_dict['id'] = egmetadata[0].id
                temp_dict['permission'] = 'edit'
                temp.append(temp_dict)

            for group in view_group:
                temp_dict = {}
                vgmetadata = sdk.search_groups(name=group)
                temp_dict['name'] = group
                temp_dict['id'] = vgmetadata[0].id
                temp_dict['permission'] = 'view'
                temp.append(temp_dict)
            folder_provision['group_permissions'] = temp
            response.append(folder_provision)
    return response


def ancestor_folder_change():
    pass
    # ancestors = sdk.folder_ancestors(folder_id=folder_id)


def provision_folders_with_group_access(
        sdk: looker_sdk,
        content_access_metadata_list: list) -> str:

    for access_item in content_access_metadata_list:

        content_metadata_id = access_item["cmi"]

        # check for existing access to the folder
        content_metadata_accesses = {
            access.group_id: access
            for access in sdk.all_content_metadata_accesses(
                content_metadata_id=content_metadata_id)}

        # sync content_metadata back to yaml file
        true_group_id = [access_item['group_permissions'][elem]['id']
                         for elem in range(0, len(access_item['group_permissions']))]
        for group_id in content_metadata_accesses.keys():
            if group_id not in true_group_id:
                delete_cmi = content_metadata_accesses.get(group_id).id
                sdk.delete_content_metadata_access(
                    content_metadata_access_id=delete_cmi)

        for elem in range(0, len(access_item['group_permissions'])):
            group_id = access_item['group_permissions'][elem]['id']
            permission = access_item['group_permissions'][elem]['permission']
            if group_id in content_metadata_accesses.keys():
                current_access = content_metadata_accesses.get(group_id)

                if current_access.permission_type == permission:
                    logger.info(
                        f'--> Group {group_id} already has access, no changes made.')

                else:
                    # don't want to inherit access from parent folders
                    sdk.update_content_metadata(
                        content_metadata_id=content_metadata_id,
                        body=models.WriteContentMeta(inherits=False)
                    )
                    try:
                        sdk.update_content_metadata_access(
                            content_metadata_access_id=current_access.id,
                            body=models.ContentMetaGroupUser(
                                content_metadata_id=content_metadata_id,
                                permission_type=permission,
                                group_id=group_id
                            ))
                    except looker_sdk.error.SDKError as foldererror:
                        logger.debug(foldererror.args[0])

                    logging.info(
                        f'--> Changed permission type to {permission}.')

            # no existing access
            # create from scratch
            else:
                # don't want to inherit access from parent folders
                sdk.update_content_metadata(
                    content_metadata_id=content_metadata_id,
                    body=models.WriteContentMeta(inherits=False)
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
                break
