import logging
import time
import coloredlogs
from looker_sdk import models
import looker_sdk

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


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
