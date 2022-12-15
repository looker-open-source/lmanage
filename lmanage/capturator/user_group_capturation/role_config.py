import logging
import coloredlogs
import itertools
from time import sleep
from lmanage.utils import errorhandling
from lmanage.utils.errorhandling import return_sleep_message

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')


class LookerPermissionSet():
    def __init__(self, permissions, name):
        self.permissions = permissions
        self.name = name


class LookerModelSet():
    def __init__(self, models, name):
        self.models = models
        self.name = name


class LookerRoles():
    def __init__(self, permission_set, model_set, teams, name):
        self.permission_set = permission_set
        self.model_set = model_set
        self.teams = teams
        self.name = name


class ExtractRoleInfo():
    def __init__(self, sdk):
        self.sdk = sdk
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
            temp = {}
            temp['name'] = role.permission_set.name
            temp['permissions'] = role.permission_set.permissions
            response.append(temp)
        return response

    def extract_permission_sets(self):
        response = []
        p_list = errorhandling.dedup_list_of_dicts(
            self.create_list_of_permission_sets())
        for role in p_list:
            logger.debug(role)
            perm_set = LookerPermissionSet(
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
        role_list = errorhandling.dedup_list_of_dicts(
            self.create_list_of_roles())
        for role in role_list:
            model_set = LookerModelSet(
                models=role.get('models'), name=role.get('name'))
            response.append(model_set)
        return response

    def extract_role_info(self):
        response = []
        for role in self.role_base:
            groups = None
            while groups is None:
                try:
                    groups = self.sdk.role_groups(role_id=role.id)
                except:
                    return_sleep_message()
            role_groups = [group.name for group in groups]

            lookerrole = LookerRoles(permission_set=role.permission_set.name,
                                     model_set=role.model_set.name, teams=role_groups, name=role.name)
            response.append(lookerrole)

        return response
