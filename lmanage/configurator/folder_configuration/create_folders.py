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


    def check_folder(self, folder_name: str, parent_folder_name: str, existing_instance_folders: dict) -> bool:
        '''
        take the existing folder name
        check it against the existing folders created and
        check it against the parent id name
        if exists return False else return true
        '''
        if folder_name in existing_instance_folders.keys():
            if parent_folder_name == 'Shared':
                parent_ids = ['1']
            else:
                search_folder_response = self.sdk.search_folders(name=parent_folder_name)
                parent_ids = [fmeta.id for fmeta in search_folder_response]

            for pid in parent_ids:
                test = self.sdk.folder_children_search(
                    folder_id=pid,
                    name=folder_name) 
                if test: 
                    resp = {}
                    resp['parent_id']=pid
                    resp['folder_name'] = folder_name
                    return resp
            return False
             
        
    def create_folder(self,
                      folder_name: str,
                      parent_folder_name: str, 
                      existing_instance_folders: dict) -> dict:
    
        chk_parent = self.check_folder(
            folder_name, 
            parent_folder_name, 
            existing_instance_folders)
        if bool(chk_parent):
            if parent_folder_name == 'Shared':
                folder = self.sdk.search_folders(name = folder_name, parent_id='1')
                return folder
            else:
                '''if parents are many, how do i know what parent is correct'''
                folder = self.sdk.search_folders(
                    name = folder_name, 
                    parent_id=chk_parent.get('parent_id'))             
                logger.warn('Not creating folder %s, with parent %s as it exists already', folder_name, parent_folder_name)
            
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

    def create_looker_folder_metadata(self, unique_folder_list: list, 
                                      data_storage: list,
                                      existing_instance_folders:dict) -> list:

        all_folders = self.get_all_folders()
        for folder in unique_folder_list:
            fname = folder.get('name')
            pid = folder.get('parent_id')
            lid = folder.get('legacy_id')
            if lid == '1':
                logger.info('Default Shared folder will not be created')
            else:
                fmetadata = self.create_folder(
                    folder_name=fname, parent_folder_name=pid, existing_instance_folders=all_folders)
                fmetadata = fmetadata[0] if isinstance(fmetadata, list) else fmetadata
                all_folders[fname] = fmetadata.id
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
        for folder_tree in self.folder_metadata:
            self.create_looker_folder_metadata(
                folder_tree, folder_metadata_list, existing_instance_folders=all_folders)
        self.sync_folders(created_folder=folder_metadata_list)
