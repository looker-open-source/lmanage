import logging
import coloredlogs

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
    def __init__(self, permission_set, model_set, team, name):
        self.permission_set = permission_set
        self.model_set = model_set
        self.team = team
        self.name = name


class ExtractRoleInfo():
    def __init__(self, sdk):
        self.sdk = sdk
        self.role_base = self.get_all_roles()

    def get_all_roles(self):
        sdk = self.sdk

        response = sdk.all_roles()
        return response

    def extract_permission_sets(self):
        response = []
        for role in self.role_base:
            perm_set = LookerPermissionSet(
                permissions=role.permission_set.permissions,
                name=role.permission_set.name)
            response.append(perm_set)
        return response

    def extract_model_sets(self):
        response = []
        for role in self.role_base:
            model_set = LookerModelSet(
                models=role.model_set.models, name=role.model_set.name)
            response.append(model_set)
        return response

    def extract_role_info(self):
        response = []
        for role in self.role_base:
            groups = self.sdk.role_groups(role_id=role.id)
            role_groups = [group.name for group in groups]

            lookerrole = LookerRoles(permission_set=role.permission_set.name,
                                     model_set=role.model_set.name, team=role_groups, name=role.name)
            response.append(lookerrole)

        return response
    # def extract_role_info(self):
    #     output = {}
    #     role_title = 'roles'
    #     output[role_title] = {}
    #     role_base = self.role_base
    #     role_base.pop(0)
    #     for role in role_base:
    #         output[role_title][role.name] = {}
    #         output[role_title][role.name]['permission_set'] = role.permission_set.name
    #         output[role_title][role.name]['model_set'] = role.model_set.name

    #         groups = self.sdk.role_groups(role_id=role.id)
    #         role_groups = [group.name for group in groups]
    #         output[role_title][role.name]['team'] = role_groups

    #     return output

    # def extract_permission_sets(self):
    #     output = {}
    #     perm_title = 'permission_sets'
    #     output[perm_title] = {}

    #     for role in self.role_base:
    #         permission_set = role.permission_set
    #         perm_string = 'permissions'
    #         output[perm_title][permission_set.name] = {}
    #         output[perm_title][permission_set.name][perm_string] = {}
    #         output[perm_title][permission_set.name][perm_string] = permission_set.permissions

    #     return output

#     def extract_model_sets(self):
#         output = {}
#         perm_title = 'model_sets'
#         output[perm_title] = {}

#         for role in self.role_base:
#             model_set = role.model_set
#             perm_string = 'models'
#             output[perm_title][model_set.name] = {}
#             output[perm_title][model_set.name][perm_string] = {}
#             output[perm_title][model_set.name][perm_string] = model_set.models

#         return output
