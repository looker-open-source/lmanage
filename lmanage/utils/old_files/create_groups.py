import logging
import coloredlogs
from looker_sdk import models
import looker_sdk

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


def create_group_if_not_exists(
        sdk: looker_sdk,
        group_name: str) -> dict:
    """ Create a Looker Group and add Group attributes

    :param str group_name: Name of a Looker group to create.
    :param dict attributes: Dictionary of attribute names and values (default is None).
    :rtype: Looker Group object.
    """
    # get group if exists
    group = sdk.search_groups(name=group_name)
    if group:
        logger.info(f"Group {group_name} already exists")
        group = group[0]
    else:
        logger.info(f'Creating group "{group_name}"')
        group = sdk.create_group(
            body=models.WriteGroup(
                can_add_to_content_metadata=True,
                name=group_name
            )
        )
    return group


def delete_groups(
        sdk: looker_sdk,
        group_config: dict):
    """ Delete groups not in the group configuration

    :param dict group_config: Dictionary of configurations for each group,
        with group names as keys.
    """
    group_names = [group_name for group_name, _ in group_config.items()]
    groups_to_delete = {group.id: group.name
                        for group in sdk.all_groups()
                        if group.name not in group_names
                        }
    for gid, gname in groups_to_delete.items():
        sdk.delete_group(gid)
        print(f'* Deleted group {gname}')


def search_group_id(sdk: looker_sdk, group_config: dict) -> list:
    group_metadata = []
    for group_name, group_info in group_config.items():
        if 'folder' in group_name:
            logger.debug(group_name)
            folder_name = group_info['folder']['name']
            group = create_group_if_not_exists(sdk, folder_name)
            temp = {}
            temp['group_id'] = group.id
            temp['group_name'] = group.name
            logger.info(f'creating folder {folder_name}')
            try:
                folder = sdk.create_folder(
                    body=models.Folder(
                        name=folder_name,
                        parent_id=1
                    )
                )
                temp['folder_id'] = folder.id
                temp['content_metadata_id'] = folder.content_metadata_id
            except looker_sdk.error.SDKError:
                logger.info('folder has already been created')
                folder = sdk.search_folders(name=folder_name)
                temp['folder_id'] = folder[0]['id']
                temp['content_metadata_id'] = folder[0]['content_metadata_id']
            group_metadata.append(temp)

        else:
            group = create_group_if_not_exists(sdk, group_name)
            logger.info(group)
            temp = {}
            temp['group_id'] = group.id
            temp['group_name'] = group.name
            group_metadata.append(temp)
    return group_metadata
