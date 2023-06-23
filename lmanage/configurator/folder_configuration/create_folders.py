from looker_sdk import models, error
from tqdm import tqdm
from lmanage.utils import logger_creation as log_color
#logger = log_color.init_logger(__name__, logger_level)


class CreateInstanceFolders():
    def __init__(self, folder_metadata, sdk, logger):
        self.sdk = sdk
        self.folder_metadata = folder_metadata
        self.logger = logger

    def get_all_folders(self):
        instance_folders = self.sdk.all_folders()
        response = {folder.id: folder.name for folder in instance_folders}
        return response

    def scour_folder(self):
        exempt_folders = ['1', '2', '3', '4', 'lookml']
        folders = self.get_all_folders()
        error_count = 0
        #allowed_folders = [folder_obj for folder_obj in folders.keys() if folder_obj not in exempt_folders]
        while error_count < 1:
            folders = self.get_all_folders()
            x = [folder_obj for folder_obj in folders.keys(
            ) if folder_obj not in exempt_folders]
        #for fid in tqdm(allowed_folders):
            try:
                self.sdk.delete_folder(folder_id=x[0])
                self.logger.debug('deleting folder %s to start afresh',
                            folders.get(x[0]))
            except error.SDKError as e:
                self.logger.error(e)
                error_count = 1

    def unnest_folder_data(self, folder_data):
        for d in tqdm(folder_data, desc = "Unesting Folder Data", unit=" unested", colour="#2c8558"):
            folder_dict = d
            metadata_list = []
            metadata_list = self.walk_folder_structure(
                dict_obj=folder_dict,
                data_storage=metadata_list,
                parent_name='1')

        self.logger.debug('retrieved yaml folder files')
        self.logger.debug('folder metadata = %s', metadata_list)

        return metadata_list

    def walk_folder_structure(self,
                              dict_obj: dict,
                              data_storage: list,
                              parent_name: str):
        folder_name = dict_obj.get('name')

        try:
            if parent_name == 'Shared':
                self.logger.debug(
                    f'Creating folder Shared Child Folder "{folder_name}"')
                folder = self.create_folder(
                    folder_name=folder_name, parent_id='1')
                new_folder_id = folder.get('id')
            elif parent_name == '1':
                folder = self.sdk.folder(folder_id='1')
                new_folder_id = 'Shared'
            else:
                folder = self.create_folder(folder_name=folder_name,
                                            parent_id=parent_name)
                new_folder_id = folder.get('id')

            temp = {}
            temp['name'] = folder_name
            temp['old_folder_id'] = dict_obj.get('id')
            temp['new_folder_id'] = new_folder_id
            temp['content_metadata_id'] = folder.get('content_metadata_id')
            temp['team_edit'] = dict_obj.get('team_edit')
            temp['team_view'] = dict_obj.get('team_view')
            self.logger.debug('data_structure to be appended = %s', temp)
            data_storage.append(temp)
        except error.SDKError as e:
            self.logger.warn('error %s', e)
            self.logger.warn(
                'you have a duplicate folder called %s with the same parent, this is against best practice and LManage is ignoring it', folder_name)

        if isinstance(dict_obj.get('subfolder'), list):
            for subfolder in dict_obj.get('subfolder'):
                self.walk_folder_structure(subfolder, data_storage,
                                           parent_name=new_folder_id)

        return data_storage

    def create_folder(self,
                      folder_name: str,
                      parent_id: str,
                      ):
        self.logger.debug(f'Creating folder "{folder_name}"')
        folder = self.sdk.create_folder(
            body=models.CreateFolder(
                name=folder_name,
                parent_id=parent_id
            )
        )
        return folder

    def sync_folders(self, created_folder: list):
        all_folders = self.sdk.all_folders()
        created_folder_ids = [fobj.get('folder_id') for fobj in created_folder]
        all_folder_ids = []

        for folder in all_folders:
            if folder.is_personal:
                pass
            elif folder.parent_id is None:
                pass
            else:
                all_folder_ids.append(folder.id)

        for fids in all_folder_ids:
            if fids not in created_folder_ids:
                try:
                    self.sdk.delete_folder(folder_id=fids)
                    self.logger.debug(
                        'deleting folder %s to sync with yaml config', fids)

                except error.SDKError as InheritanceError:
                    self.logger.debug('root folder has been deleted so %s',
                                InheritanceError)
        return 'your folders are in sync with your yaml file'

    def create_folders(self):
        folder_metadata_list = []
        all_folders = self.get_all_folders()
        self.scour_folder()
        created_folder_metadata = self.unnest_folder_data(
            folder_data=self.folder_metadata)
        return created_folder_metadata

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
