from looker_sdk import models, error
import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')


class GetRoleBase():
    def __init__(self, sdk) -> None:
        self.sdk = sdk

    def get_all_roles(self):
        sdk = self.sdk

        r = sdk.all_roles()
        return r


class ExtractRoleInfo():
    def __init__(self, sdk, role_base):
        self.sdk = sdk
        self.role_base = role_base

    def extract_permission_sets(self):
        output = {}
        perm_title = 'permission_sets'
        output[perm_title] = {}

        for role in self.role_base:
            permission_set = role.permission_set
            perm_string = 'permissions'
            output[perm_title][permission_set.name] = {}
            output[perm_title][permission_set.name][perm_string] = {}
            output[perm_title][permission_set.name][perm_string] = permission_set.permissions

        return output

    def extract_model_sets(self):
        output = {}
        perm_title = 'model_sets'
        output[perm_title] = {}

        for role in self.role_base:
            model_set = role.model_set
            perm_string = 'models'
            output[perm_title][model_set.name] = {}
            output[perm_title][model_set.name][perm_string] = {}
            output[perm_title][model_set.name][perm_string] = model_set.models

        return output

    def extract_role_info(self):
        output = {}
        role_title = 'roles'
        output[role_title] = {}
        role_base = self.role_base
        role_base.pop(0)
        for role in role_base:
            output[role_title][role.name] = {}
            output[role_title][role.name]['permission_set'] = role.permission_set.name
            output[role_title][role.name]['model_set'] = role.model_set.name

            groups = self.sdk.role_groups(role_id=role.id)
            role_groups = [group.name for group in groups]
            output[role_title][role.name]['team'] = role_groups

        return output
