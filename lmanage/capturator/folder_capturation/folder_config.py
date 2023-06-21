from yaspin import yaspin
from lmanage.utils import looker_object_constructors as loc, errorhandling as eh, logger_creation as log_color
from looker_sdk import error
from tqdm import tqdm
from tenacity import retry, wait_random, wait_fixed, stop_after_attempt



class CaptureFolderConfig():
    ''' Class to read in folder metadata and unested_folder_data '''

    def __init__(self, sdk, logger):
        self.sdk = sdk
        self.logger = logger

    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def get_all_folders(self) -> list:
        response = self.sdk.all_folders()
        return response

    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def get_folder_metadata(self, folder_id: str) -> list:
        response = self.sdk.folder(folder_id)
        return response

    def get_clean_folders(self) -> list:
        '''retriving all Looker instance folder id and creating a dict of folder to root folder'''
        system_folder_id = ['1', '2', '3', '4', '5', 'lookml']
        all_folder_metadata = None
        while all_folder_metadata is None:
            try:
                with yaspin().white.bold.shark.on_blue as sp:
                    sp.text = f"getting folder metadata"
                    all_folder_metadata = self.get_all_folders()
            except error.SDKError as e:
                self.logger.debug(e)
        all_folder_metadata = [
            folder.id for folder in all_folder_metadata if not folder.is_personal if not folder.is_personal_descendant if not folder.is_embed if folder.id not in system_folder_id]
        return all_folder_metadata

    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def get_all_content_metadata_accesses(self, cmi: int) -> dict:
        response = self.sdk.all_content_metadata_accesses(
            content_metadata_id=cmi)
        return response

    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def get_group_metadata(self, gid: int) -> dict:
        response = self.sdk.group(
            group_id=gid)
        return response

    def get_content_access_metadata(self, cmi, root_folder: bool):
        r = []
        cmi_metadata = None
        if root_folder:
            cmi_metadata = self.get_all_content_metadata_accesses(cmi=1)
        else:
            cmi_metadata = self.get_all_content_metadata_accesses(cmi=cmi)

        for cmi in cmi_metadata:
            group_id = cmi.group_id
            if group_id is not None:
                permission_type = cmi.permission_type.value
                temp = {}
                group_meta = self.get_group_metadata(gid=group_id)
                temp[permission_type] = group_meta.get('name')
                r.append(temp)
            else:
                self.logger.info(
                    'no group permissions set on folder, ignoring individual permissions')
                pass
        return r

    def create_folder_objects(self, folder_list):
        '''creating folder objects (class in utils folder)'''
        response = {}
        folder_list = sorted(folder_list, key=int, reverse=True)
        for folder in tqdm(folder_list, desc="Folder Capturation", unit=" folders", colour="#2c8558"):
            f_metadata = self.get_folder_metadata(folder_id=folder)

            if f_metadata.name in ['Shared', 'Users']:
                folder_name = f_metadata.name
                f_metadata.name = '%s_' % folder_name
                self.logger.debug(f_metadata)

            if f_metadata.is_personal or f_metadata.is_personal_descendant or f_metadata.is_embed:
                self.logger.debug(
                    'folder %s  will be ignored as it\'s a personal folder or embed folder', f_metadata.name)
            else:
                content_metadata_id = f_metadata.get('content_metadata_id')
                a_list = self.get_content_access_metadata(
                    cmi=content_metadata_id, root_folder=False)

                created_folder_object = loc.LookerFolder(
                    id=folder, folder_metadata=f_metadata, access_list=a_list)
                self.logger.debug('capturing folder %s', f_metadata.get('name'))
                response[folder] = created_folder_object

        root_content_meta = self.get_content_access_metadata(
            cmi=1, root_folder=True)
        root_f_meta = self.get_folder_metadata(folder_id=str(1))

        root_folder = loc.LookerFolder(
            id='1', folder_metadata=root_f_meta, access_list=root_content_meta)
        response['1'] = root_folder
        return response

    @ staticmethod
    def get_highest_folders(folder_list):
        '''helper to isolate highest level folders and return as a list'''
        response = [
            folder for folder in folder_list if folder.parent_id == '1']
        return response

    @ staticmethod
    def get_subfolders(folder_list, parent_id):
        '''helper function to get all subfolders for a given parent'''
        response = []
        for folder in folder_list:
            if folder.parent_id == parent_id:
                response.append(folder)
        return response

    def create_nested_folder_objects(self, folder_list):
        '''create folder objects list with all children attached return
        full list of instance folder structure'''
        for f in folder_list:
            folder = folder_list.get(f)
            f_parent_id = folder.parent_id

            if f_parent_id in list(folder_list.keys()):
                parent_folder = folder_list.get(f_parent_id)
                parent_folder.add_child_folder(folder)
            else:
                pass

        # folder_list = [f for f in list(
        #     folder_list.values()) if f.parent_id == '1']
        folder_list = [f for f in list(folder_list.values()) if f.id == '1']

        return folder_list

    def execute(self):
        '''main function to do chain all the processes'''
        clean_folders = self.get_clean_folders()
        created_folder_list = self.create_folder_objects(
            folder_list=clean_folders)
        final_folder_list = self.create_nested_folder_objects(
            folder_list=created_folder_list)
        return clean_folders, final_folder_list
