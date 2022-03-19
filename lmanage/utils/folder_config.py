import looker_sdk
from looker_sdk import models
import coloredlogs
import logging

from looker_sdk.sdk.api31.models import DataActionFormSelectOption

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


def get_unique_folders(
        sdk: looker_sdk,
        parsed_yaml: dict) -> list:

    folder_metadata = []
    for k, v in parsed_yaml.items():
        if 'folder' in k:
            folder_name = parsed_yaml[k]['folder']['name']
            folder_metadata.append(folder_name)

    return folder_metadata


def create_folder_if_not_exists(
        sdk: looker_sdk,
        folder_name: str,
        parent_id: str) -> dict:

    folder = sdk.search_folders(name=folder_name)

    if folder:
        logger.info(f"Folder {folder_name} already exists")
        folder = folder[0]
    else:
        if parent_id == '1':
            pass
        else:
            parent_id = sdk.search_folders(name=parent_id)[0].id

        logger.info(f'Creating folder "{folder_name}"')
        folder = sdk.create_folder(
            body=models.CreateFolder(
                name=folder_name,
                parent_id=parent_id
            )
        )
    return folder


def create_looker_folder_metadata(
        sdk: looker_sdk,
        unique_folder_list: list) -> list:

    folder_metadata = []

    for folder_group in unique_folder_list:
        for folder in folder_group:
            fname = folder.get('name')
            pid = folder.get('parent_id')
            fmetadata = create_folder_if_not_exists(
                sdk=sdk, folder_name=fname, parent_id=pid)
            temp = {}
            temp['folder_id'] = fmetadata.id
            temp['folder_name'] = fmetadata.name
            temp['content_metadata_id'] = fmetadata.content_metadata_id
            temp['team_edit'] = folder.get('team_edit')
            temp['team_view'] = folder.get('team_view')
            folder_metadata.append(temp)

    return folder_metadata


def sync_folders(
        sdk: looker_sdk,
        folder_metadata_list: list,
        folder_name_list: list) -> str:

    all_folders = sdk.all_folders()
    folder_dict = {}

    for folder in all_folders:
        if folder.is_personal:
            pass
        elif folder.parent_id is None:
            pass
        else:
            folder_dict[folder.name] = folder.id

    for folder_name in folder_dict.keys():
        if folder_name not in folder_name_list:
            sdk.delete_folder(folder_id=folder_dict[folder_name])
            logger.info(
                f'deleting folder {folder_name} to sync with yaml config')

    return 'your folders are in sync with your yaml file'


def get_folder_metadata(
        parsed_yaml: dict):
    folder_metadata = []
    for k, v in parsed_yaml['folder_permissions'].items():
        if 'folder' in k:
            folder_metadata.append(v[0])
    response = []

    for d in folder_metadata:
        metadata_list = []
        metadata_list = walk_folder_structure(
            dict_obj=d, data_storage=metadata_list, parent_id='1')
        response.append(metadata_list)

    return response


def walk_folder_structure(dict_obj: dict, data_storage: list, parent_id: str):
    temp = {}
    temp['name'] = dict_obj.get('name')
    temp['team_edit'] = dict_obj.get('team_edit')
    temp['team_view'] = dict_obj.get('team_view')
    temp['parent_id'] = parent_id
    logger.debug(f'data_structure to be appended = {temp}')
    data_storage.append(temp)

    if isinstance(dict_obj.get('subfolder'), list):
        for subfolder in dict_obj.get('subfolder'):
            walk_folder_structure(subfolder, data_storage,
                                  parent_id=dict_obj.get('name'))

    return data_storage
