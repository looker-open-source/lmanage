import logging
import time
import coloredlogs
from looker_sdk import models
import looker_sdk
from folder_configuration.folder_config import CreateInstanceFolders

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


class CreateAndProvisionInstanceFolders(CreateInstanceFolders):
    def __init__(self, folders, sdk):
        super().__init__(folders, sdk)
        self.instance_folder_metadata = super().execute()

    def execute(self):
        print('hugo')
        x = self.instance_folder_metadata
        return super().execute()

    def get_content_access_metadata(
            sdk: looker_sdk,
            instance_folder_metadata: list) -> list:
        response = []

        for folder in instance_folder_metadata:
            temp_dict = {}
            temp_dict['name'] = folder.get('folder_name')
            temp_dict['cmi'] = folder.get('content_metadata_id')
            edit_group = folder.get('team_edit')
            view_group = folder.get('team_view')

            perms = []
            if isinstance(edit_group, list):
                for group in edit_group:
                    group_dict = {}
                    egmetadata = sdk.search_groups(name=group)
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
                    vgmetadata = sdk.search_groups(name=group)
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

    def create_content_metadata_access(
            sdk: looker_sdk,
            group_id: int,
            permission_input: str,
            content_metadata_id: int) -> dict:

        sdk.create_content_metadata_access(
            body=models.ContentMetaGroupUser(
                content_metadata_id=content_metadata_id,
                permission_type=permission_input,
                group_id=group_id
            )
        )
        folder = sdk.content_metadata(
            content_metadata_id=content_metadata_id).name
        group = sdk.search_groups(id=group_id)[0].name
        logger.info(
            f'''--> Successfully permissioned group {group} with {permission_input} access, on folder {folder}.''')

    def check_existing_access(
            sdk: looker_sdk,
            content_metadata_id: int) -> dict:
        # check for existing access to the folder
        response = {
            access.group_id: access
            for access in sdk.all_content_metadata_accesses(
                content_metadata_id=content_metadata_id)}
        return response

    def check_folder_ancestors(
            sdk: looker_sdk,
            group_id: int,
            cmaid: int):

        folder_id = sdk.content_metadata(content_metadata_id=cmaid).folder_id
        ancestors_list = sdk.folder_ancestors(folder_id=folder_id)
        ancestors_list = [
            folder for folder in ancestors_list if folder.id != '1']

        for ancestor in ancestors_list:
            ancestor_cmaid = ancestor.content_metadata_id
            folder_access = check_existing_access(
                sdk=sdk,
                content_metadata_id=ancestor_cmaid)
            if group_id not in folder_access:
                if check_folder_inheritance(
                        sdk=sdk, content_metadata_id=ancestor_cmaid):
                    update_folder_inheritance(
                        sdk=sdk, cmaid=ancestor_cmaid, inheritance=False)

                    create_content_metadata_access(
                        sdk=sdk,
                        group_id=group_id,
                        permission_input='view',
                        content_metadata_id=ancestor_cmaid)
                    update_folder_inheritance(
                        sdk=sdk, cmaid=ancestor_cmaid, inheritance=True)
                else:
                    create_content_metadata_access(
                        sdk=sdk,
                        group_id=group_id,
                        permission_input='view',
                        content_metadata_id=ancestor_cmaid)

    def check_folder_inheritance(
            sdk: looker_sdk,
            content_metadata_id: int) -> bool:
        response = sdk.content_metadata(
            content_metadata_id=content_metadata_id)
        r = response.inherits
        return r

    def check_folder_inheritance_change(
            sdk: looker_sdk,
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

    def update_folder_inheritance(
            sdk: looker_sdk,
            cmaid: int,
            inheritance: bool):

        # don't want to inherit access from parent folders
        sdk.update_content_metadata(
            content_metadata_id=cmaid,
            body=models.WriteContentMeta(inherits=inheritance)
        )

    def add_content_access(
            sdk: looker_sdk,
            cm_accesses: dict,
            cmaid: int,
            group_permissions: list) -> dict:

        for group in group_permissions:
            group_id = group.get('id')
            permission = group.get('permission')
            check_folder_ancestors(
                sdk=sdk,
                group_id=group_id,
                cmaid=cmaid
            )
            update_folder_inheritance(
                sdk=sdk,
                cmaid=cmaid,
                inheritance=False
            )
            folder_name = sdk.content_metadata(
                content_metadata_id=cmaid).name
            group_name = sdk.search_groups(id=group_id)[0].name

            if group_id in cm_accesses.keys():
                current_access = cm_accesses.get(group_id)

                if current_access.permission_type == permission:
                    logger.info(
                        f'''--> Group {group_name} already has access, to folder {folder_name}
                        no changes made.''')

                else:
                    try:
                        sdk.update_content_metadata_access(
                            content_metadata_access_id=current_access.id,
                            body=models.ContentMetaGroupUser(
                                content_metadata_id=cmaid,
                                permission_type=permission,
                                group_id=group_id
                            ))
                    except looker_sdk.error.SDKError as foldererror:
                        logger.debug(foldererror.args[0])
                    folder_name = sdk.content_metadata(
                        content_metadata_id=cmaid).name
                    group_name = sdk.search_groups(id=group_id)[0].name

                    logging.info(
                        f'--> Updating group id {group_name} permission type to {permission} on folder {folder_name}.')

            # no existing access
            # create from scratch
            elif permission == 'no_permission':
                pass
            else:
                create_content_metadata_access(
                    sdk=sdk,
                    content_metadata_id=cmaid,
                    permission_input=permission,
                    group_id=group_id
                )

    def provision_folders_with_group_access(
            sdk: looker_sdk,
            content_access_metadata_list: list) -> str:

        for access_item in content_access_metadata_list:
            content_metadata_id = access_item["cmi"]

            update_folder_inheritance(
                sdk=sdk, cmaid=content_metadata_id, inheritance=False)

            gp_permissions = access_item.get('group_permissions')

            sync_folder_permission(sdk=sdk,
                                   cmaid=content_metadata_id,
                                   gp_permissions=gp_permissions)

    def remove_content_access(
            sdk: looker_sdk,
            cm_accesses: dict):

        # remove all accesses
        for group_id in cm_accesses.keys():
            try:
                delete_cmi = cm_accesses.get(group_id).id
                sdk.delete_content_metadata_access(
                    content_metadata_access_id=delete_cmi)
            except looker_sdk.error.SDKError as error:
                logger.info(f'''You have an inheritance error in your YAML file possibly 
                            around {delete_cmi}, skipping group_id {group_id}''')

    def sync_folder_permission(
        sdk: looker_sdk,
        cmaid: int,
            gp_permissions: list):

        # check for existing access to the folder
        content_metadata_accesses = check_existing_access(
            sdk=sdk, content_metadata_id=cmaid)

        # check group permissions and add back 1 by 1
        gp_permissions = [
            perms for perms in gp_permissions if perms.get('id') != 'no_id']

        if len(gp_permissions) == 0:
            update_folder_inheritance(
                sdk=sdk, cmaid=cmaid, inheritance=True)
            update_folder_inheritance(sdk=sdk, cmaid=cmaid, inheritance=False)
        else:
            # remove folder content accesses
            remove_content_access(
                sdk=sdk, cm_accesses=content_metadata_accesses)
            # check for existing access to the folder
            content_metadata_accesses = check_existing_access(
                sdk=sdk, content_metadata_id=cmaid)

            add_content_access(
                sdk=sdk,
                cm_accesses=content_metadata_accesses,
                cmaid=cmaid,
                group_permissions=gp_permissions)

    def remove_all_user_group(
            sdk: looker_sdk,
            content_access_metadata_list: list):

        # remove parent Shared group instance access
        try:
            sdk.update_content_metadata_access(
                content_metadata_access_id=1,
                body=models.ContentMetaGroupUser(
                    permission_type='view',
                    content_metadata_id=1,
                    group_id=1
                )
            )
        except looker_sdk.error.SDKError:
            logger.info('All Users group already configured')
        clean = list()
        for avt in content_access_metadata_list:
            temp = {}
            temp['name'] = avt['name']
            temp['cmi'] = avt['cmi']
            clean.append(temp)
        res_list = [i for n, i in enumerate(clean) if i not in clean[n + 1:]]

        for access_item in res_list:
            time.sleep(1)

            content_metadata_id = access_item["cmi"]

            # check for existing access to the folder
            content_metadata_accesses = {
                access.group_id: access
                for access in sdk.all_content_metadata_accesses(
                    content_metadata_id=content_metadata_id)}

            for id, value in content_metadata_accesses.items():
                logger.debug(f'Checking item {value.id}')
                if value.group_id == 1:
                    cmaid = value.id
                    sdk.delete_content_metadata_access(
                        content_metadata_access_id=cmaid)
