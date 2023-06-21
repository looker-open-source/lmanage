import logging
from tqdm import tqdm
from lmanage.utils import looker_object_constructors as loc, errorhandling as eh, logger_creation as log_color

#logger = log_color.init_logger(__name__, logger_level)


class ExtractRoleInfo():
    def __init__(self, sdk, logger):
        self.sdk = sdk
        self.logger = logger
        self.role_base = self.get_all_roles()

    def get_all_roles(self):
        sdk = self.sdk
        response = sdk.all_roles()
        for role in enumerate(response):

            if role[1].name == 'Admin':
                response.pop(role[0])

        return response

    def create_list_of_permission_sets(self):
        response = []
        for role in self.role_base:
            if role.permission_set is None:
                raise Exception(f'role name {role.name} has no permission_set, please add one to be captured or delete the role')
            temp = {}
            temp['name'] = role.permission_set.name
            temp['permissions'] = role.permission_set.permissions
            response.append(temp)
        return response

    def extract_permission_sets(self):
        response = []
        p_list = eh.dedup_list_of_dicts(
            self.create_list_of_permission_sets())
        for role in p_list:
            self.logger.debug(role)
            perm_set = loc.LookerPermissionSet(
                name=role.get('name'),
                permissions=role.get('permissions'))
            response.append(perm_set)

        return response

    def create_list_of_roles(self):
        response = []
        for role in self.role_base:
            temp = {}
            temp['name'] = role.model_set.name
            temp['models'] = role.model_set.models
            response.append(temp)
        return response

    def extract_model_sets(self):
        response = []
        role_list = eh.dedup_list_of_dicts(
            self.create_list_of_roles())
        for role in role_list:
            model_set = loc.LookerModelSet(
                models=role.get('models'), name=role.get('name'))
            response.append(model_set)
        return response

    def extract_role_info(self):
        response = []
        for role in tqdm(self.role_base, desc = "Role Capture", unit=" roles", colour="#2c8558"):
            groups = None
            trys = 0
            while groups is None:
                trys += 1
                try:
                    groups = self.sdk.role_groups(role_id=role.id)
                except:
                    eh.return_sleep_message(call_number=trys)
            role_groups = [group.name for group in groups]

            lookerrole = loc.LookerRoles(permission_set=role.permission_set.name,
                                     model_set=role.model_set.name, teams=role_groups, name=role.name)
            response.append(lookerrole)

        return response
