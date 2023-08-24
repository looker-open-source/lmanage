from looker_sdk import models, error
from tqdm import tqdm
from lmanage.utils import logger_creation as log_color
import typing
# logger = log_color.init_logger(__name__, logger_level)


class CreateInstanceFolders():
    def __init__(self, folder_metadata, sdk, logger):
        self.sdk = sdk
        self.folder_metadata = folder_metadata
        self.logger = logger

    def create_folders(self):
        self.__delete_top_level_folders()
        for folder_tree in tqdm(self.folder_metadata, desc="Unesting Folder Data", unit="unested", colour="#2c8558"):
            metadata_list = []
            metadata_list = self.__walk_folder_structure(
                folder_tree=folder_tree, data_storage=metadata_list)
        self.logger.debug('Retrieved YAML folder files')
        self.logger.debug(f'Older metadata = {metadata_list}')
        return metadata_list

    def create_folder_mapping_dict(self, folder_metadata: list) -> dict:
        '''
        create a folder mapping dict with legacy folder id as it's key and new folder id as the value for use in content migration
        '''
        response = {}
        for folder_obj in folder_metadata:
            lid = folder_obj.get('old_folder_id')
            fid = folder_obj.get('new_folder_id')
            response[lid] = fid

        return response

    def __delete_top_level_folders(self):
        def is_top_level_folder(folder):
            return folder['parent_id'] is not None and int(folder['parent_id']) == 1
        all_folders = self.sdk.all_folders('id, name, parent_id')
        for folder in tqdm(all_folders):
            if is_top_level_folder(folder):
                try:
                    self.logger.debug(
                        f'Deleting folder "{folder["name"]}"')
                    self.sdk.delete_folder(folder_id=folder['id'])
                except error.SDKError as e:
                    self.logger.error(e)

    def __walk_folder_structure(self, folder_tree: dict, data_storage: list, parent_id: typing.Optional[str] = None):
        folder_name = folder_tree.get('name')
        try:
            if parent_id is None:
                folder_id = '1'
            else:
                folder_id = self.__create_folder(folder_name=folder_name,
                                                 parent_id=parent_id).get('id')
            temp = {
                'name': folder_name,
                'old_folder_id': folder_tree.get('id'),
                'new_folder_id': folder_id,
                'content_metadata_id': folder_tree.get('content_metadata_id'),
                'team_view': folder_tree.get('team_view'),
                'team_edit': folder_tree.get('team_edit'),
            }
            self.logger.debug(f'Data structure to be appended = {temp}')
            data_storage.append(temp)
            if isinstance(folder_tree.get('subfolder'), list):
                for subfolder in folder_tree.get('subfolder'):
                    self.__walk_folder_structure(subfolder, data_storage,
                                                 parent_id=folder_id)
        except error.SDKError as e:
            self.logger.warn('error %s', e)
            self.logger.warn(
                'you have a duplicate folder called %s with the same parent, this is against best practice and LManage is ignoring it', folder_name)

        # if isinstance(dict_obj.get('subfolder'), list):
        #     for subfolder in dict_obj.get('subfolder'):
        #         self.walk_folder_structure(subfolder, data_storage,
        #                                    parent_name=new_folder_id)

        return data_storage

    def __create_folder(self, folder_name: str, parent_id: str):
        self.logger.debug(f'Creating folder "{folder_name}"')
        folder = self.sdk.create_folder(
            body=models.CreateFolder(
                name=folder_name,
                parent_id=parent_id
            )
        )
        return folder

    # def sync_folders(self, created_folder: list):
    #     all_folders = self.sdk.all_folders()
    #     created_folder_ids = [fobj.get('folder_id') for fobj in created_folder]
    #     all_folder_ids = []

    #     for folder in all_folders:
    #         if folder.is_personal:
    #             pass
    #         elif folder.parent_id is None:
    #             pass
    #         else:
    #             all_folder_ids.append(folder.id)

    #     for fids in all_folder_ids:
    #         if fids not in created_folder_ids:
    #             try:
    #                 self.sdk.delete_folder(folder_id=fids)
    #                 self.logger.debug(
    #                     'deleting folder %s to sync with yaml config', fids)

    #             except error.SDKError as InheritanceError:
    #                 self.logger.debug('root folder has been deleted so %s',
    #                                   InheritanceError)
    #     return 'your folders are in sync with your yaml file'
