import logging
import coloredlogs
import looker_sdk
from looker_sdk import models
from role_config import CreateRoleBase

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')


class CreateInstanceRoles(CreateRoleBase):
    def __init__(self, roles, sdk):
        self.role_metadata = roles
        self.sdk = sdk

    def create_permission_lookup(self):
        all_permission_sets = self.get_all_permission_sets()
        instance_permission_set_dict = {
            perm.name: perm.id for perm in all_permission_sets}
        return instance_permission_set_dict

    def create_model_lookup(self):
        all_model_sets = self.get_all_model_sets()
        instance_model_set_dict = {
            model.name: model.id for model in all_model_sets}
        return instance_model_set_dict

    def create_allgroup_lookup(self):
        all_groups = self.sdk.all_groups()
        group_dict = {group.name: group.id for group in all_groups}
        return group_dict

    def create_allrole_lookup(self):
        all_roles = self.sdk.all_roles()
        role_dict = {role.name: role.id for role in all_roles}
        return role_dict

    def create_instance_roles(self):
        model_lookup = self.create_model_lookup()
        permission_lookup = self.create_permission_lookup()

        role_output = []

        for role_name, metadata in self.role_metadata.items():
            model_set_id = model_lookup.get(metadata.get('model_set'))
            permission_set_id = permission_lookup.get(
                metadata.get('permission_set'))

            body = models.WriteRole(
                name=role_name,
                permission_set_id=permission_set_id,
                model_set_id=model_set_id
            )
            try:
                role = self.sdk.create_role(
                    body=body
                )
            except looker_sdk.error.SDKError as roleerror:
                logger.debug(roleerror)
                role_id = self.sdk.search_roles(name=role_name)[0].id
                role = self.sdk.update_role(role_id=role_id, body=body)
            temp = {}
            temp['role_id'] = role.id
            temp['role_name'] = role_name
            role_output.append(temp)
        logger.info(role_output)
        return role_output

    def set_role(self, role_id: str, group_id: list) -> str:
        try:
            self.sdk.set_role_groups(role_id, group_id)
            return logger.info(f'attributing {group_id} permissions on instance')
        except looker_sdk.error.SDKError:
            return logger.info('something went wrong')

    def attribute_instance_roles(self, created_role_metadata: list):
        role_lookup = self.create_allrole_lookup()
        group_lookup = self.create_allgroup_lookup()

        for role_name, metadata in self.role_metadata.items():
            teams = metadata.get('team')
            role_id = role_lookup.get(role_name)
            group_id_list = []
            for team in teams:
                group_id = group_lookup.get(team)
                group_id_list.append(group_id)
            self.set_role(role_id=role_id, group_id=group_id_list)

    def sync_roles(self):
        all_role_lookup = self.create_allrole_lookup()
        all_role_lookup.pop('Admin')
        yaml_role = [role for role in self.role_metadata]
        logger.debug(all_role_lookup)

        for role_name in all_role_lookup.keys():
            if role_name not in yaml_role:
                role_id = self.sdk.search_roles(name=role_name)[0].id
                self.sdk.delete_role(role_id=role_id)

    def execute(self):
        created_roles = self.create_instance_roles()
        self.attribute_instance_roles(created_role_metadata=created_roles)
        self.sync_roles()
