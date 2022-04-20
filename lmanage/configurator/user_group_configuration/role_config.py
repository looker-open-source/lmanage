from looker_sdk import models, error
import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')


class CreateRoleBase():
    def __init__(self, permissions, model_sets, sdk):
        self.permission_set_metadata = permissions
        self.model_set_metadata = model_sets
        self.sdk = sdk

    def create_permission_set(self, sdk, permission_set_list: list):

        final_response = []
        for permission in permission_set_list:
            permission_set_name = permission.get('role_name')
            permissions = permission.get('permission')
            body = models.WritePermissionSet(
                name=permission_set_name.lower(),
                permissions=permissions
            )
            try:
                perm = sdk.create_permission_set(
                    body=body
                )
            except error.SDKError:
                perm = sdk.search_permission_sets(name=permission_set_name)[0]
                pid = perm.id
                perm = sdk.update_permission_set(
                    permission_set_id=pid, body=body)

            temp = {}
            temp['name'] = perm.name
            temp['pid'] = perm.id
            final_response.append(temp)

        logger.debug(final_response)
        return final_response

    def sync_permission_set(self, sdk, all_perms, permission_set_list: list):

        permissions_dict = {p.name: p.id for p in}
        permissions_dict.pop('Admin')
        yaml_permissions = [role.get('name') for role in permission_set_list]

        for permission_set_name in permissions_dict.keys():

            if permission_set_name not in yaml_permissions:
                permission_id = sdk.search_permission_sets(
                    name=permission_set_name)[0].id
                sdk.delete_permission_set(permission_set_id=permission_id)

    def create_model_set(self, sdk, model_set_list: list) -> list:
        final_response = []
        for model in model_set_list:
            model_set_metadata = model.get('model_set_value')
            for model_set in model_set_metadata:
                model_set_name = model_set.get('name')
                attributed_models = model_set.get('models')
                body = models.WriteModelSet(
                    name=model_set_name.lower(), models=attributed_models)
                try:
                    model = sdk.create_model_set(body=body)
                except error.SDKError as modelerror:
                    logger.info(modelerror.args[0])
                    model = sdk.search_model_sets(name=model_set_name)[0]
                    model_set_id = model.id
                    model = sdk.update_model_set(
                        model_set_id=model_set_id, body=body)
                temp = {}
                temp['model_set_name'] = model.name
                temp['model_set_id'] = model.id
                final_response.append(temp)
        logger.info(final_response)
        return final_response

    def sync_model_set(self, sdk, all_models, model_set_list: list):

        model_sets_dict = {p.name: p.id for p in all_models}
        model_sets_dict.pop('All')
        yaml_model = [role.get('model_set_name') for role in model_set_list]

        for model_set_name in model_sets_dict.keys():

            if model_set_name not in yaml_model:
                model_id = sdk.search_model_sets(
                    name=model_set_name)[0].id
                sdk.delete_model_set(model_set_id=model_id)

    def get_all_permission_sets(self):
        sdk = self.sdk
        r = sdk.all_permission_sets()
        return r

    def get_all_model_sets(self):
        sdk = self.sdk
        r = sdk.all_model_sets()
        return r

    def create_role_building_blocks(self):
        # Creating permission sets if they don't exits already on instance
        self.create_permission_set(
            sdk=self.sdk, all_perms=self.get_all_permission_sets(), permission_set_list=self.permission_set_metadata)
        # Creating model set if they don't exist on Looker instance
        self.create_model_set(
            sdk=self.sdk, model_set_list=self.model_set_metadata)

        # Syncing Permission and Model sets with Yaml file.
        self.sync_permission_set(
            sdk=self.sdk, permission_set_list=self.permission_set_metadata)
        self.sync_model_set(
            sdk=self.sdk, all_models=self.get_all_model_sets(), model_set_list=self.model_set_metadata)
