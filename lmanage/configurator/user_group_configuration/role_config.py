from looker_sdk import models, error
from lmanage.utils import errorhandling as eh
from lmanage.utils import logger_creation as log_color
from tqdm import tqdm
from tenacity import retry, wait_random, wait_fixed, stop_after_attempt

#logger = log_color.init_logger(__name__, logger_level)


class CreateRoleBase():
    def __init__(self, logger, permissions, model_sets, sdk):
        self.permission_set_metadata = permissions
        self.model_set_metadata = model_sets
        self.sdk = sdk
        self.logger = logger

    def create_permission_set(self, sdk, permission_set_dict: dict):

        final_response = []
        for permission in tqdm(permission_set_dict, desc="Creating Permission Sets", unit=" perm sets", colour="#2c8558"):
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
                    self.logger.debug(permerr)
                    err_msg = eh.return_error_message(permerr)
                    self.logger.debug(permerr)
                    self.logger.debug(
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

        self.logger.debug(final_response)
        return final_response

    def sync_permission_set(self, sdk, all_perms, permission_set_dict: dict):

        permissions_dict = {p.name: p.id for p in all_perms}
        permissions_dict.pop('Admin')
        yaml_permissions = [permission.get('name').lower()
                            for permission in permission_set_dict]
        self.logger.debug('yaml permissions configured = %s', yaml_permissions)
        self.logger.debug('existing permsissions = %s', permissions_dict.keys())

        for permission_set_name in permissions_dict.keys():

            if permission_set_name.lower() not in yaml_permissions:
                permission_id = permissions_dict.get(permission_set_name)
                sdk.delete_permission_set(permission_set_id=permission_id)

    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def search_looker_model_set(self, sdk, model_set_name: str):
        model_set_id = sdk.search_model_sets(name=model_set_name)[0].id
        return model_set_id

    # @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def create_looker_model_set(self, body: models.WriteModelSet):
        sdk = self.sdk
        model = sdk.create_model_set(body=body)
        return model

    def create_model_set(self, sdk, model_set_dict: list) -> list:
        final_response = []
        model_set_dict = eh.dedup_list_of_dicts(model_set_dict)
        for model in tqdm(model_set_dict, desc="Creating Model Sets", unit=" model sets", colour="#2c8558"):
            model_set_name = model.get('name')
            attributed_models = model.get('models')
            body = models.WriteModelSet(
                name=model_set_name.lower(), models=attributed_models)
            try:
                model_set_id = self.create_looker_model_set(body=body).id
                temp = {}
                final_response.append(temp)
            except error.SDKError as modelerror:
                err_msg = eh.return_error_message(modelerror)
                self.logger.debug(
                    'you have a warning in creating model set %s, warning = %s', model_set_name, err_msg)
                self.logger.debug(modelerror)
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
                    self.logger.debug(
                        'The model %s, has encountered a warning, warning = %s', model_set_name, err_msg)
                    temp = {}
                    temp['model_set_name'] = model.name
                    temp['model_set_id'] = model.id
                    final_response.append(temp)

        self.logger.debug(final_response)
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

    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
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
