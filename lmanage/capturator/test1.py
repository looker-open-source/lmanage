class LookerFolder(object):
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.children = []
        self.parent = None

    def __repr__(self):
        return f"I am folder {self.id}"

    def add_parent(self, ref):
        self.parent = ref

    def add_child(self, ref):
        self.children.append(ref)


class LookerFolderManager(object):
    def __init__(self):
        self.folders = []

    def __repr__(self) -> str:
        return f"{self.folders}"

    def add_folder(self, ref):
        self.folders.append(ref)

    def create_link(self, folder1, folder2):
        folder1.add_parent(folder2)
        folder2.add_child(folder1)


Tree = LookerFolderManager()
Folder1 = LookerFolder('foo', 1)
Folder2 = LookerFolder('bar', 2)
Tree.add_folder(Folder1)
Tree.add_folder(Folder2)
Tree.create_link(Folder1, Folder2)

print(Tree)

# def recursive_create(root):
#     for folder in root.children:
#         folder.use_api_to_create_self()
#         if folder.children is not None:
#             for child in folder:
#    def get_folder_ancestors(self, folder_id_dict):
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
        removal_folder_id = ['1', '2', 'lookml']
        r = []
        for elem in enumerate(folder_list):
            check_value = list(elem[1].values())[0]
            if check_value in removal_folder_id or check_value is None:
                logger.info('cleaning folder list')
            else:
                r.append(elem[1])
        return r

                 return recursive_create(child)
    def clean_fldlist(self, folder_list):
        keys_index_dict = self.get_keys_index(folder_list=folder_list)

        return keys_index_dict.get(None)

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
    def create_folder_structure(self, folder_structure_dict):
        r = []
        folder_structure_dict = self.clean_folder_list(
            folder_list=folder_structure_dict)
        for struct in folder_structure_dict:
            pid = list(struct.values())[0]
            folder = loc.LookerFolder(sdk=self.sdk, id=pid)
            logger.info(f'adding folder {pid}')
            # subfolderid = list(struct.keys())[0]
            # logger.info(f'adding subfolder {subfolderid}')

            # folder.add_child(sid=subfolderid)

            # for altparents in folder_structure_dict:
            #     alt_pid = list(altparents.values())[0]
            #     if pid == alt_pid and struct != altparents:
            #         folder.add_child(sid=list(altparents.keys())[0])

            r.append(folder)

        return r


