import logging
from looker_sdk import models, error
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')
logging.getLogger("requests").setLevel(logging.WARNING)


class CreateInstanceFolders():
    def __init__(self, folder_metadata, sdk):
        self.sdk = sdk
        self.folder_metadata = folder_metadata

    def get_all_folders(self):
        instance_folders = self.sdk.all_folders()
        response = {folder.name: folder.id for folder in instance_folders}
        return response

    def create_folder_if_not_exists(self,
                                    folder_name: str,
                                    parent_folder_name: str) -> dict:

        existing_instance_folders = self.get_all_folders()

        if folder_name in existing_instance_folders:
            logger.warning(
                'folder %s already exists on current instance', folder_name)
            folder = self.sdk.search_folders(name=folder_name)[0]
            return folder
        else:
            if parent_folder_name == '1':
                logger.warning(
                    f"Folder {folder_name} is a top level folder")
                folder = self.sdk.create_folder(
                    body=models.CreateFolder(
                        name=folder_name,
                        parent_id=parent_folder_name
                    )
                )
                return folder

            else:
                parent_id = existing_instance_folders.get(parent_folder_name)

                logger.info(f'Creating folder "{folder_name}"')
                folder = self.sdk.create_folder(
                    body=models.CreateFolder(
                        name=folder_name,
                        parent_id=parent_id
                    )
                )
                return folder

    def create_looker_folder_metadata(self, unique_folder_list: list, data_storage: list) -> list:

        for folder in unique_folder_list:
            fname = folder.get('name')
            pid = folder.get('parent_id')
            lid = folder.get('legacy_id')
            if lid == '1':
                logger.info('Default Shared folder will not be created')
            else:
                fmetadata = self.create_folder_if_not_exists(
                    folder_name=fname, parent_folder_name=pid)
                temp = {}
                temp['folder_id'] = fmetadata.id
                temp['folder_name'] = fmetadata.name
                temp['content_metadata_id'] = fmetadata.content_metadata_id
                temp['team_edit'] = folder.get('team_edit')
                temp['team_view'] = folder.get('team_view')
                data_storage.append(temp)
        return data_storage

    def sync_folders(self, created_folder: list):
        all_folders = self.sdk.all_folders()
        folder_dict = {}

        folder_metadata_list = {
            folder.get('folder_name'): folder.get('folder_id') for folder in created_folder}

        for folder in all_folders:
            if folder.is_personal:
                pass
            elif folder.parent_id is None:
                pass
            else:
                folder_dict[folder.name] = folder.id

        for folder_name in folder_dict.keys():
            if folder_name not in folder_metadata_list.keys():
                try:
                    self.sdk.delete_folder(folder_id=folder_dict[folder_name])
                    logger.info(
                        'deleting folder %s to sync with yaml config', folder_name)

                except error.SDKError as InheritanceError:
                    logger.info('root folder has been deleted so %s',
                                InheritanceError)
        return 'your folders are in sync with your yaml file'

    def execute(self):
        folder_metadata_list = []
        for folder_tree in self.folder_metadata:
            self.create_looker_folder_metadata(
                folder_tree, folder_metadata_list)
        self.sync_folders(created_folder=folder_metadata_list)
