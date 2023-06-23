import logging
import time
from looker_sdk import models, error
from lmanage.utils import errorhandling
from tqdm import tqdm
from lmanage.utils.errorhandling import return_sleep_message
from lmanage.utils import logger_creation as log_color
from tenacity import retry, wait_fixed, wait_random, stop_after_attempt

class CreateAndProvisionInstanceFolders():
    def __init__(self, folders, sdk, logger):
        self.sdk = sdk
        self.instance_folder_metadata = folders
        self.logger = logger

    def get_content_access_metadata(self, folder: dict) -> list:
        response = []

        folder_list = self.sdk.all_folders()
        folder_cmaid_lookup = {
            folder.name: folder.content_metadata_id for folder in folder_list}

        folder_name = folder.get('name')
        cmaid = folder_cmaid_lookup.get(folder_name)
        temp_dict = {}
        temp_dict['name'] = folder_name
        temp_dict['cmi'] = cmaid
        edit_group = folder.get('team_edit')
        view_group = folder.get('team_view')

        perms = []
        if isinstance(edit_group, list):
            for group in edit_group:
                group_dict = {}
                egmetadata = self.search_looker_groups(name=group)
                group_dict['name'] = group
                group_dict['id'] = egmetadata[0].id
                group_dict['permission'] = 'edit'
                perms.append(group_dict)
        else:
            group_dict = {}
            group_dict['name'] = 'no_name'
            group_dict['id'] = 'no_id'
            group_dict['permission'] = 'no_permission'
            perms.append(group_dict)

        if isinstance(view_group, list):
            for group in view_group:
                group_dict = {}
                vgmetadata = self.search_looker_groups(name=group)
                group_dict['name'] = group
                group_dict['id'] = vgmetadata[0].id
                group_dict['permission'] = 'view'
                perms.append(group_dict)
        else:
            group_dict = {}
            group_dict['name'] = 'no_name'
            group_dict['id'] = 'no_id'
            group_dict['permission'] = 'no_permission'
            perms.append(group_dict)

        temp_dict['group_permissions'] = perms
        response.append(temp_dict)
        return response
    
    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def create_content_metadata_access(
        self,
            group_id: int,
            permission_input: str,
            content_metadata_id: int) -> dict:

        self.sdk.create_content_metadata_access(
            body=models.ContentMetaGroupUser(
                content_metadata_id=content_metadata_id,
                permission_type=permission_input,
                group_id=group_id
            )
        )
        folder = self.sdk.content_metadata(
            content_metadata_id=content_metadata_id).name
        group = self.search_looker_groups(id=group_id)[0].name
        self.logger.debug(
            f'''--> Successfully permissioned group {group} with {permission_input} access, on folder {folder}.''')

    def check_existing_access(self,
                              content_metadata_id: int) -> dict:
        # check for existing access to the folder
        response = {
            access.group_id: access
            for access in self.sdk.all_content_metadata_accesses(
                content_metadata_id=content_metadata_id)}
        return response


    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def check_folder_ancestors(self,
                               group_id: int,
                               cmaid: int):
        '''
        This method
        '''

        # getting folder id from content metadata number
        folder_id = self.sdk.content_metadata(
            content_metadata_id=cmaid).folder_id
        # returning the folder ancestors of the folder (i.e. all folders preceding)
        ancestors_list = self.sdk.folder_ancestors(folder_id=folder_id)
        # refining list to eliminate the Shared folder
        ancestors_list = [
            folder for folder in ancestors_list if folder.id != '1']

        # looping through folder ancestors checking their access corresponds with yaml access, if not update
        for ancestor in ancestors_list:
            ancestor_cmaid = ancestor.content_metadata_id
            folder_access = self.check_existing_access(
                content_metadata_id=ancestor_cmaid)
            # if this condition is met then do nothing
            if group_id not in folder_access:
                if self.check_folder_inheritance(
                        content_metadata_id=ancestor_cmaid):
                    # N.B. when you update folder inheritance you will create a content metadata access
                    # so recheck value to prevent trying to set an already set value
                    self.update_folder_inheritance(
                        cmaid=ancestor_cmaid, inheritance=False)
                    folder_access = self.check_existing_access(
                        content_metadata_id=ancestor_cmaid)
                    if folder_access:
                        pass
                    else:
                        self.create_content_metadata_access(
                            group_id=group_id,
                            permission_input='view',
                            content_metadata_id=ancestor_cmaid)
                        self.update_folder_inheritance(
                            cmaid=ancestor_cmaid, inheritance=True)
                else:
                    self.create_content_metadata_access(
                        group_id=group_id,
                        permission_input='view',
                        content_metadata_id=ancestor_cmaid)

    def check_folder_inheritance(self,
                                 content_metadata_id: int) -> bool:
        response = self.sdk.content_metadata(
            content_metadata_id=content_metadata_id)
        r = response.inherits
        return r

    def check_folder_inheritance_change(self,
                                        folder_input: dict) -> bool:
        check = []
        perms = folder_input['group_permissions']
        for permission in perms:
            if permission['permission'] == 'view':
                check.append('true')
            elif permission['permission'] == 'edit':
                check.append('true')
            else:
                check.append('false')

        if 'true' in check:
            return True
        else:
            return False

    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def update_folder_inheritance(
            self,
            cmaid: int,
            inheritance: bool):
        # don't want to inherit access from lmanage.parent folders
        self.sdk.update_content_metadata(
            content_metadata_id=cmaid,
            body=models.WriteContentMeta(inherits=inheritance)
        )

    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def search_looker_groups(self, id=None, name=None) -> list:
        if id is not None:
            return self.sdk.search_groups(id=id)
        elif name is not None:
            return self.sdk.search_groups(name=name)

    def add_content_access(
        self,
            cm_accesses: dict,
            cmaid: int,
            group_permissions: list) -> dict:

        for group in group_permissions:
            group_id = group.get('id')
            permission = group.get('permission')
            self.check_folder_ancestors(
                group_id=group_id,
                cmaid=cmaid
            )
            self.update_folder_inheritance(
                cmaid=cmaid,
                inheritance=False
            )
            group_name = self.search_looker_groups(id=group_id)[0].name
            self.logger.debug(group_name)

            if group_id in cm_accesses.keys():
                current_access = cm_accesses.get(group_id)

                if current_access.permission_type == permission:
                    self.logger.debug(
                        f'''--> Group {group_name} already has access, to folder {folder_name}
                        no changes made.''')

                else:
                    try:
                        self.sdk.update_content_metadata_access(
                            content_metadata_access_id=current_access.id,
                            body=models.ContentMetaGroupUser(
                                content_metadata_id=cmaid,
                                permission_type=permission,
                                group_id=group_id
                            ))
                    except error.SDKError as foldererror:
                        self.logger.debug(foldererror)
                    folder_name = self.sdk.content_metadata(
                        content_metadata_id=cmaid).name
                    group_name = self.search_looker_groups(id=group_id)[0].name

                    self.logger.debug(
                        f'--> Updating group id {group_name} permission type to {permission} on folder {folder_name}.')

            # no existing access
            # create from lmanage.scratch
            elif permission == 'no_permission':
                pass
            else:
                self.create_content_metadata_access(
                    content_metadata_id=cmaid,
                    permission_input=permission,
                    group_id=group_id
                )

    def provision_folders_with_group_access(self, content_access_metadata_list: list):

        for folder_tree in tqdm(content_access_metadata_list, desc="Folder Perms - Group Access", unit=" folders provisioned", colour="#2c8558"):

            for access_item in folder_tree:
                content_metadata_id = access_item["cmi"]

                self.update_folder_inheritance(
                    cmaid=content_metadata_id, inheritance=False)

                gp_permissions = access_item.get('group_permissions')

                self.sync_folder_permission(cmaid=content_metadata_id,
                                            gp_permissions=gp_permissions)

    def remove_content_access(self,
                              cm_accesses: dict):

        # remove all accesses
        for group_id in cm_accesses.keys():
            try:
                delete_cmi = cm_accesses.get(group_id).id
                self.sdk.delete_content_metadata_access(
                    content_metadata_access_id=delete_cmi)
            except error.SDKError as InheritanceError:
                self.logger.debug('''You have an inheritance error in your YAML file possibly 
                            around %s, skipping group_id %s''', delete_cmi, group_id)
                self.logger.debug(InheritanceError)

    def sync_folder_permission(
        self,
        cmaid: int,
            gp_permissions: list):

        # check for existing access to the folder
        content_metadata_accesses = self.check_existing_access(
            content_metadata_id=cmaid)

        # check group permissions and add back 1 by 1
        gp_permissions = [
            perms for perms in gp_permissions if perms.get('id') != 'no_id']

        self.logger.debug(
            'syncing folder permissions for content metadata id %s', cmaid)

        if not gp_permissions:
            self.update_folder_inheritance(
                cmaid=cmaid, inheritance=True)
            self.update_folder_inheritance(cmaid=cmaid, inheritance=False)
        else:
            # remove folder content accesses
            self.remove_content_access(
                cm_accesses=content_metadata_accesses)
            # check for existing access to the folder
            content_metadata_accesses = self.check_existing_access(
                content_metadata_id=cmaid)

            self.add_content_access(
                cm_accesses=content_metadata_accesses,
                cmaid=cmaid,
                group_permissions=gp_permissions)

    def remove_all_user_group(
        self,
            content_access_metadata_list: list):

        # remove parent Shared group instance access
        try:
            folder = '1'
            self.sdk.update_content_metadata_access(
                content_metadata_access_id=folder,
                body=models.ContentMetaGroupUser(
                    permission_type='view',
                    content_metadata_id=folder,
                    group_id=folder
                )
            )
        except error.SDKError:
            self.logger.debug('All Users group already configured')
        clean = list()
        for avt in content_access_metadata_list:
            temp = {}
            temp['name'] = avt[0].get('name')
            temp['cmi'] = avt[0].get('cmi')
            clean.append(temp)
        res_list = [i for n, i in enumerate(clean) if i not in clean[n + 1:]]

        for access_item in res_list:
            time.sleep(1)

            content_metadata_id = access_item["cmi"]

            # check for existing access to the folder
            content_metadata_accesses = {
                access.group_id: access
                for access in self.sdk.all_content_metadata_accesses(
                    content_metadata_id=content_metadata_id)}

            for id, value in content_metadata_accesses.items():
                self.logger.debug(f'Checking item {value.id}')
                if value.group_id == 1:
                    cmaid = value.id
                    self.sdk.delete_content_metadata_access(
                        content_metadata_access_id=cmaid)

    def execute(self):
        # CONFIGURE FOLDERS WITH EDIT AND VIEW ACCESS
        content_access_metadata = []
        for folder_obj in tqdm(self.instance_folder_metadata, desc="Folder Perms - Edit/View Access", unit=" folders", colour="#2c8558"):
            r = self.get_content_access_metadata(folder=folder_obj)
            content_access_metadata.append(r)

        # ADD AND SYNC CONTENT VIEW ACCESS WITH YAML
        self.provision_folders_with_group_access(
            content_access_metadata_list=content_access_metadata)
        self.remove_all_user_group(
            content_access_metadata_list=content_access_metadata)
