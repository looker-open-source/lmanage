from looker_sdk import models, error
import logging
import coloredlogs
from lmanage.utils import errorhandling as eh

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')


class CreateRoleBase():
    def __init__(self, permissions, model_sets, sdk):
        self.permission_set_metadata = permissions
        self.model_set_metadata = model_sets
        self.sdk = sdk

    def create_permission_set(self, sdk, permission_set_dict: dict):

        final_response = []
        for permission in permission_set_dict:
            permission_set_name = permission.get('name')
            if permission_set_name == 'Admin':
                pass
            else:
                permissions = permission.get('permissions')
                body = models.WritePermissionSet(
                    name=permission_set_name.lower(),
                    permissions=permissions
                )
                try:
                    perm = sdk.create_permission_set(
                        body=body
                    )
                except error.SDKError as permerr:
                    logger.debug(permerr)
                    err_msg = eh.return_error_message(permerr)
                    logger.debug(permerr)
                    logger.warn(
                        'you have a warning permission set %s, warning = %s already exists on this instance', permission_set_name, err_msg)

                    perm = sdk.search_permission_sets(
                        name=permission_set_name)[0]
                    pid = perm.id
                    perm = sdk.update_permission_set(
                        permission_set_id=pid, body=body)

                temp = {}
                temp['name'] = perm.name
                temp['pid'] = perm.id
                final_response.append(temp)

        logger.debug(final_response)
        return final_response

    def sync_permission_set(self, sdk, all_perms, permission_set_dict: dict):

        permissions_dict = {p.name: p.id for p in all_perms}
        permissions_dict.pop('Admin')
        yaml_permissions = [permission.get('name').lower()
                            for permission in permission_set_dict]
        logger.debug('yaml permissions configured = %s', yaml_permissions)
        logger.debug('existing permsissions = %s', permissions_dict.keys())

        for permission_set_name in permissions_dict.keys():

            if permission_set_name.lower() not in yaml_permissions:
                permission_id = permissions_dict.get(permission_set_name)
                sdk.delete_permission_set(permission_set_id=permission_id)

    def create_model_set(self, sdk, model_set_dict: list) -> list:
        final_response = []
        model_set_dict = eh.dedup_list_of_dicts(model_set_dict)
        for model in model_set_dict:
            model_set_name = model.get('name')
            attributed_models = model.get('models')
            body = models.WriteModelSet(
                name=model_set_name.lower(), models=attributed_models)
            try:
                model = sdk.create_model_set(body=body)
                temp = {}
                final_response.append(temp)
            except error.SDKError as modelerror:
                err_msg = eh.return_error_message(modelerror)
                logger.warn(
                    'you have a warning in creating model set %s, warning = %s', model_set_name, err_msg)
                logger.debug(modelerror)
                model = sdk.search_model_sets(name=model_set_name)[0]
                model_set_id = model.id
                try:
                    model = sdk.update_model_set(
                        model_set_id=model_set_id, body=body)

                    temp = {}
                    temp['model_set_name'] = model.name
                    temp['model_set_id'] = model.id
                    final_response.append(temp)
                except error.SDKError as txt:
                    err_msg = eh.return_error_message(txt)
                    logger.warn(
                        'The model %s, has encountered a warning, warning = %s', model_set_name, err_msg)
                    temp = {}
                    temp['model_set_name'] = model.name
                    temp['model_set_id'] = model.id
                    final_response.append(temp)

        logger.debug(final_response)
        return final_response

    def sync_model_set(self, sdk, all_models, model_set_list: list):
        model_sets_dict = {p.name: p.id for p in all_models}
        model_sets_dict.pop('All')
        yaml_model = [model.get('name').lower() for model in model_set_list]

        for model_set_name in model_sets_dict.keys():

            if model_set_name.lower() not in yaml_model:
                model_id = model_sets_dict.get(model_set_name)
                sdk.delete_model_set(model_set_id=model_id)

    def get_all_permission_sets(self):
        sdk = self.sdk
        r = sdk.all_permission_sets()
        return r

    def get_all_model_sets(self):
        sdk = self.sdk
        r = sdk.all_model_sets()
        return r

    def execute(self):
        # Creating permission sets if they don't exits already on instance
        self.create_permission_set(
            sdk=self.sdk, permission_set_dict=self.permission_set_metadata)
        # Creating model set if they don't exist on Looker instance
        self.create_model_set(
            sdk=self.sdk, model_set_dict=self.model_set_metadata)

        # Syncing Permission and Model sets with Yaml file.
        self.sync_permission_set(
            sdk=self.sdk, all_perms=self.get_all_permission_sets(), permission_set_dict=self.permission_set_metadata)
        self.sync_model_set(sdk=self.sdk, all_models=self.get_all_model_sets(
        ), model_set_list=self.model_set_metadata)
