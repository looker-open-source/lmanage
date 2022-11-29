import logging
import coloredlogs
import itertools
from time import sleep
from utils.errorhandling import return_sleep_message

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

    def check_permission_set(self, role, r_list):
        for r_list_val in r_list:
            if role.permission_set.name == r_list_val.name:
                if role.permission_set.permissions == r_list_val.permissions:
                    return False
            else:
                return True
        return True

    def extract_permission_sets(self):
        response = []
        for role in self.role_base:
            logger.debug(role)
            if role.permission_set is None or role.model_set is None:
                del_id = self.sdk.search_roles(name=role.name)[0].id
                self.sdk.delete_role(role_id=str(del_id))
            else:
                if self.check_permission_set(role, response):
                    perm_set = LookerPermissionSet(
                        permissions=role.permission_set.permissions,
                        name=role.permission_set.name)
                    response.append(perm_set)

        return response

    def check_model_set(self, role, r_list):
        for r_list_val in r_list:
            if role.model_set.name == r_list_val.name:
                if role.model_set.models == r_list_val.models:
                    return False
            else:
                return True
        return True

    def extract_model_sets(self):
        response = []
        for role in self.role_base:
            if self.check_model_set(role=role, r_list=response):
                model_set = LookerModelSet(
                    models=role.model_set.models, name=role.model_set.name)
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
