import logging
from os import name
from looker_sdk import models, error
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
        instance_folders = self.sdk.all_folders()
        response = {folder.id: folder.name for folder in instance_folders}
        return response

    def get_folder_ancestors(self, folder_id_dict):
        r = []
        for fid in folder_id_dict:
            x = {}
            f_metadata = self.sdk.folder(folder_id=fid)
            if f_metadata.child_count == 0:
                x[f_metadata.id] = f_metadata.parent_id
                r.append(x)
                ancestors = self.sdk.folder_ancestors(folder_id=fid)
                for ancestor_folder in ancestors:
                    y = {}
                    y[ancestor_folder.id] = ancestor_folder.parent_id
                    r.append(y)
        return_list = []
        for i in range(len(r)):
            if r[i] not in r[i + 1:]:
                return_list.append(r[i])
        return return_list

    def clean_folder_list(self, folder_list):
        removal_folder_id = ['1', '2']
        r = []
        for elem in enumerate(folder_list):
            check_value = list(elem[1].values())[0]
            print(check_value)
            if check_value in removal_folder_id or check_value is None:
                print('nope')

            else:
                r.append(elem[1])
        return r

    def create_folder_structure(self, folder_structure_dict):
        r = []
        folder_structure_dict = self.clean_folder_list(
            folder_list=folder_structure_dict)
        for struct in folder_structure_dict:
            pid = list(struct.values())[0]
            folder = loc.LookerFolder(sdk=self.sdk, id=pid)
            subfolderid = list(struct.keys())[0]
            folder.add_child(sid=subfolderid)

            for altparents in folder_structure_dict:
                alt_pid = list(altparents.values())[0]
                if pid == alt_pid and struct != altparents:
                    folder.add_child(sid=list(altparents.keys())[0])

            r.append(folder)

        return r

    def clean_fldlist(self, folder_list):
        keys_index_dict = self.get_keys_index(folder_list=folder_list)

        return keys_index_dict.get(None)

    def sort_folder_list(self, folder_list):
        test = self.get_keys_index(folder_list=folder_list)
        return [i for i in sorted(test.keys(), reverse=True)]

    def get_keys_index(self, folder_list):
        return {folder.id: folder_list.index(folder) for folder in folder_list}

    def get_keys(self, dict_obj):
        return list(dict_obj.keys())[0]

    def get_values(self, dict_obj):
        return list(dict_obj.values())[0]

    def iterate_over_subfolders(self, subfolder_list_obj, elem_key, elem_values):
        output = []
        for folder_id in subfolder_list_obj:
            if folder_id == elem_key:
                temp = {}
                temp[folder_id] = elem_values
                output.append(temp)
            else:
                output.append(folder_id)
        return output

    def iterate_over_folderlist(self, list_obj, element_key, element_value):
        for d in list_obj:
            c_key = self.get_keys(d)
            subfolders = self.get_values(d)
            new_values = self.iterate_over_subfolders(
                subfolder_list_obj=subfolders, elem_key=element_key, elem_values=element_value)
            d[c_key] = new_values

        return list_obj

    # def walk_folder_structure(self, list_obj, used_list):
    #     ''' Get values of Last Element and add Element to used list '''
    #     first_elem_key = self.get_keys(list_obj[0])
    #     first_elem_values = self.get_values(list_obj[0])
    #     used_list.append(first_elem_key)

    #     ''' create system to be able to delete items from original list '''
    #     keys_dict = self.get_keys_index(list_obj)
    #     key_list = list(keys_dict.keys())

    #     ''' check if key is in any of the subfolder values '''
    #     self.iterate_over_folderlist(
    #         list_obj=list_obj, element_key=first_elem_key, element_value=first_elem_values)
    #     if first_elem_key in key_list:
    #         list_obj.pop(keys_dict.get(first_elem_key))

    #     if len(list_obj) == 1:
    #         # if list(list_obj[0].keys())[0] == 1:
    #         return list_obj
    #     else:
    #         self.walk_folder_structure(list_obj=list_obj, used_list=used_list)
    def get_highest_folders(self, folder_list):
        r = [folder for folder in folder_list if folder.parent_id == 1]
        return r

    def sort_folders_stuff(self, folder_list):
        checklist = self.get_highest_folders(folder_list=folder_list)

        for folder in enumerate(folder_list):
            comparitor = folder[1].id

            for comparison in folder_list:
                if comparitor == comparison.parent_id:
                    folder[1].add_child_folder(comparison)
                    folder_list.remove(folder)
                    if len(checklist) == len(folder_list):
                        return folder_list
                    else:
                        self.sort_folders_stuff(folder_list=folder_list)

    def execute(self):
        folders = self.get_all_folders()
        folder_structure_dict = self.get_folder_ancestors(
            folder_id_dict=folders)
        folder_structure = self.create_folder_structure(
            folder_structure_dict=folder_structure_dict)

        sortedfolderlist = self.sort_folder_list(folder_list=folder_structure)
        self.sort_folders_stuff(folder_list=folder_structure)
        # self.walk_folder_structure(list_obj=attibuted_folder_structure, used_list=[])

        return folder_structure
