import logging
import coloredlogs
from lmanage.utils import looker_object_constructors as loc
from lmanage.utils.errorhandling import return_sleep_message

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')
logging.getLogger("requests").setLevel(logging.WARNING)


class CaptureFolderConfig():
    ''' Class to read in folder metadata and unested_folder_data '''

    def __init__(self, sdk):
        self.sdk = sdk

    def get_all_folders(self):
        '''retriving all Looker instance folders'''
        instance_folders = None
        while instance_folders is None:
            try:
                instance_folders = self.sdk.all_folders()
            except:
                return_sleep_message()
        response = [
            folder.id for folder in instance_folders if folder.parent_id != "2" if folder.parent_id != "3"]
        return response

    @staticmethod
    def clean_folders(folder_list):
        '''removing standard system folders from lmanage.folder list'''
        removal_folder_id = ['1', '2', '3', '4',  'lookml', '5']
        response = []
        for elem in enumerate(folder_list):
            check_value = elem[1]
            if check_value in removal_folder_id or check_value is None:
                logger.debug(
                    'removing folder id %s from lmanage.the capturation', check_value)
            else:
                response.append(elem[1])

        response = sorted(response, reverse=True)
        return response

    def get_content_access_metadata(self, cmi, root_folder: bool):
        r = []
        cmi_metadata = None
        while cmi_metadata is None:
            try:
                if root_folder:
                    cmi_metadata = self.sdk.all_content_metadata_accesses(
                        content_metadata_id=1)
                else:
                    cmi_metadata = self.sdk.all_content_metadata_accesses(
                        content_metadata_id=cmi)
            except:
                return_sleep_message()
        for cmi in cmi_metadata:
            group_id = cmi.group_id
            if group_id is not None:
                permission_type = cmi.permission_type.value
                temp = {}
                group_meta = None
                while group_meta is None:
                    try:
                        group_meta = self.sdk.group(group_id=group_id)
                    except:
                        return_sleep_message()
                temp[permission_type] = group_meta.get('name')
                r.append(temp)
            else:
                logger.info(
                    'no group permissions set on folder, ignoring individual permissions')
                pass
        return r

    def create_folder_objects(self, folder_list):
        '''creating folder objects (class in utils folder)'''
        response = {}
        folder_list = sorted(folder_list, key=int, reverse=True)
        for folder in folder_list:
            f_metadata = None
            while f_metadata is None:
                try:
                    f_metadata = self.sdk.folder(folder_id=str(folder))
                except:
                    return_sleep_message()
            if f_metadata.name in ['Shared', 'Users']:
                folder_name = f_metadata.name
                f_metadata.name = '%s_' % folder_name
                logger.debug(f_metadata)

            if f_metadata.is_personal or f_metadata.is_personal_descendant or f_metadata.is_embed:
                logger.warn(
                    'folder %s  will be ignored as it\'s a personal folder or embed folder', f_metadata.name)
            else:
                content_metadata_id = f_metadata.get('content_metadata_id')
                a_list = self.get_content_access_metadata(
                    cmi=content_metadata_id, root_folder=False)

                created_folder_object = loc.LookerFolder(
                    id=folder, folder_metadata=f_metadata, access_list=a_list)
                logger.info('capturing folder %s', f_metadata.get('name'))
                response[folder] = created_folder_object
        root_content_meta = self.get_content_access_metadata(
            cmi=1, root_folder=True)
        root_f_meta = None
        while root_f_meta is None:
            try:
                root_f_meta = self.sdk.folder(folder_id=str(1))
            except:
                return_sleep_message()

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
        folders = self.get_all_folders()
        clean_folders = self.clean_folders(folder_list=folders)
        created_folder_list = self.create_folder_objects(
            folder_list=clean_folders)
        final_folder_list = self.create_nested_folder_objects(
            folder_list=created_folder_list)
        return final_folder_list
