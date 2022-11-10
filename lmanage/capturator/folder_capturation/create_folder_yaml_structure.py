import logging
import time
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

# folder_permissions:
#   business_operations_folder:
#   - name: 'Business Operations'
#     team_view:
#       - BusinessOperations
#     subfolder:
#       - name: test_sub
#         team_edit:
#           - Freddy
#         team_view:
#           - hugo
#   - name: 'sexy time'
#     team_edit:
#       - sexy_group1


class CreateFolderOutput():
    def __init__(self, folder_list):
        self.folder_list = folder_list

    def create_folder_structure(self, folder_obj: object, data_storage: list):
        temp = {}
        temp['name'] = folder_obj.name
        temp['permissions'] = folder_obj.content_access_list
        temp['subfolder'] = folder_obj.children
        data_storage.append(temp)

        if isinstance(folder_obj.children, list):
            for subfolder in folder_obj.children:
                self.create_folder_structure(subfolder, data_storage)

        return data_storage

    def make_dict(self):
        x = []
        f = self.folder_list

        for folders in f:
            data_storage = []
            x = self.create_folder_structure(
                folder_obj=folders, data_storage=data_storage)

        return x

    def execute(self):
        '''
        goal: extract all the folders into the appropriate markdown folder structure
        '''
        x = self.make_dict()
        return x
