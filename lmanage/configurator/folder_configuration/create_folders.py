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
        response = {folder.id: folder.name for folder in instance_folders}
        return response

    def scour_folder(self):
        exempt_folders = ['1', '2', '3', '4', 'lookml']
        folders = self.get_all_folders()
        error_count = 0
        while error_count < 1:
            folders = self.get_all_folders()
            x = [folder_obj for folder_obj in folders.keys(
            ) if folder_obj not in exempt_folders]
            try:
                self.sdk.delete_folder(folder_id=x[0])
                logger.info('deleting folder %s to start afresh',
                            folders.get(x[0]))
            except error.SDKError as e:
                logger.error(e)
                error_count = 1

    def unnest_folder_data(self, folder_data):
        response = []

        for d in folder_data:
            folder_dict = d
            metadata_list = []
            metadata_list = self.walk_folder_structure(
                dict_obj=folder_dict,
                data_storage=metadata_list,
                parent_name='1')

            response.append(metadata_list)

        logger.info('retrieved yaml folder files')
        logger.debug('folder metadata = %s', response)

        return response

    def walk_folder_structure(self,
                              dict_obj: dict,
                              data_storage: list,
                              parent_name: str):
        folder_name = dict_obj.get('name')

        
        try:
            if parent_name == 'Shared':
                logger.info(f'Creating folder Shared Child Folder "{folder_name}"')
                folder = self.create_folder(folder_name=folder_name, parent_id='1')    
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
            logger.debug('data_structure to be appended = %s', temp)
            data_storage.append(temp)            
        except error.SDKError as e:
            logger.warn('error %s', e)
            logger.warn(
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
        logger.info(f'Creating folder "{folder_name}"')
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
                    logger.info(
                        'deleting folder %s to sync with yaml config', fids)

                except error.SDKError as InheritanceError:
                    logger.info('root folder has been deleted so %s',
                                InheritanceError)
        return 'your folders are in sync with your yaml file'

    def execute(self):
        folder_metadata_list = []
        all_folders = self.get_all_folders()
        self.scour_folder()
        created_folder_metadata = self.unnest_folder_data(folder_data=self.folder_metadata)
        return created_folder_metadata
        # self.sync_folders(created_folder=folder_metadata_list)
