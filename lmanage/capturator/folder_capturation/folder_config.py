import logging
import coloredlogs
from utils import looker_object_constructors as loc

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')
logging.getLogger("requests").setLevel(logging.WARNING)


class CaptureFolderConfig():
    ''' Class to read in folder metadata and unested_folder_data '''

    def __init__(self, sdk):
        self.sdk = sdk

    def get_all_folders(self):
        '''retriving all Looker instance folders'''
        instance_folders = self.sdk.all_folders()
        response = [folder.id for folder in instance_folders]
        return response

    @staticmethod
    def clean_folders(folder_list):
        '''removing standard system folders from folder list'''
        removal_folder_id = ['1', '2', 'lookml', '5']
        response = []
        for elem in enumerate(folder_list):
            check_value = elem[1]
            if check_value in removal_folder_id or check_value is None:
                logger.info('removing folder id %s', check_value)
            else:
                response.append(elem[1])

        response = sorted(response, reverse=True)
        return response

    def get_content_access_metadata(self, cmi):
        r = []
        cmi_metadata = self.sdk.all_content_metadata_accesses(
            content_metadata_id=cmi)
        for cmi in cmi_metadata:
            group_id = cmi.group_id
            permission_type = cmi.permission_type.value
            temp = {}
            temp[permission_type] = loc.LookerGroup(
                sdk=self.sdk, id=group_id).name
            r.append(temp)

        return r

    def create_folder_objects(self, folder_list):
        '''creating folder objects (class in utils folder)'''
        response = []
        for folder in folder_list:
            f_metadata = self.sdk.folder(folder_id=str(folder))
            content_metadata_id = f_metadata.get('content_metadata_id')
            a_list = self.get_content_access_metadata(cmi=content_metadata_id)

            created_folder_object = loc.LookerFolder(
                id=folder, folder_metadata=f_metadata, access_list=a_list)
            response.append(created_folder_object)
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

    @ staticmethod
    def check_value_high(folder_list):
        '''test'''
        return [folder.id for folder in folder_list if folder.parent_id == '1']

    def create_nested_folder_objects(self, folder_list):
        '''create folder objects list with all children attached return
        full list of instance folder structure'''
        check_value = self.check_value_high(folder_list)
        iterator = 0
        while len(folder_list) > len(check_value):
            folder = folder_list[iterator]
            if folder.parent_id == '1':
                iterator += 1
                pass
            else:
                subfolders = self.get_subfolders(
                    folder_list=folder_list, parent_id=folder.parent_id)
                f_parent_id = folder.parent_id
                update_folder = [
                    f for f in folder_list if f.id == f_parent_id][0]

                for f in subfolders:
                    update_idx = folder_list.index(update_folder)
                    folder_list[update_idx].add_child_folder(f)
                    delete_idx = folder_list.index(f)
                    folder_list.pop(delete_idx)

        return folder_list

    def execute(self):
        '''main function to do chain all the processes'''
        folders = self.get_all_folders()
        clean_folders = self.clean_folders(folder_list=folders)
        created_folder_list = self.create_folder_objects(
            folder_list=clean_folders)
        self.create_nested_folder_objects(folder_list=created_folder_list)

        return created_folder_list
