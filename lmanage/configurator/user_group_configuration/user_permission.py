from looker_sdk import models, error
from lmanage.configurator.user_group_configuration.role_config import CreateRoleBase
from lmanage.utils.errorhandling import return_error_message
from tqdm import tqdm
from tenacity import retry, wait_random, wait_fixed, stop_after_attempt

class CreateInstanceRoles(CreateRoleBase):
    def __init__(self, roles, sdk, logger):
        self.role_metadata = roles
        self.sdk = sdk
        self.logger = logger

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
    
    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def update_looker_role(self, role_id: str, body: models.WriteRole):
        role = self.sdk.update_role(role_id=role_id, body=body)
        return role


    def create_instance_roles(self):
        model_lookup = self.create_model_lookup()
        permission_lookup = self.create_permission_lookup()

        role_output = []

        for r_metadata in tqdm(self.role_metadata, desc = "User Role Creation", unit=" user roles", colour="#2c8558"):
            role_name = r_metadata.get('name')
            model_set_id = model_lookup.get(
                r_metadata.get('model_set') if r_metadata.get('model_set') == 'All' else r_metadata.get('model_set').lower())
            permission_set_id = permission_lookup.get(
                r_metadata.get('permission_set').lower())
            if role_name != 'Admin':
                body = models.WriteRole(
                    name=role_name,
                    permission_set_id=str(permission_set_id),
                    model_set_id=str(model_set_id)
                )
                try:
                    role = self.sdk.create_role(
                        body=body
                    )

                except error.SDKError as roleerror:
                    err_msg = return_error_message(roleerror)
                    self.logger.debug(
                        'You have hit a warning creating your role \'%s\'; warning = %s', role_name, err_msg)
                    role_id = self.sdk.search_roles(name=role_name)[0].id
                    role = self.update_looker_role(
                        role_id=str(role_id), body=body)
                temp = {}
                temp['role_id'] = role.id
                temp['role_name'] = role_name
                role_output.append(temp)
            else:
                pass
        self.logger.debug(role_output)
        return role_output

    def set_role(self, role_id: str, group_id: list) -> str:
        try:
            self.sdk.set_role_groups(role_id, group_id)
            return self.logger.debug(f'attributing {group_id} permissions on instance')
        except error.SDKError as role_err:
            err_msg = return_error_message(role_err)
            self.logger.debug(
                'You have hit a warning setting your role, warning = %s', err_msg)
            self.logger.debug(role_err)

    def attribute_instance_roles(self, created_role_metadata: list):
        role_lookup = self.create_allrole_lookup()
        group_lookup = self.create_allgroup_lookup()

        for r_metadata in tqdm(self.role_metadata, desc = "Instance Role Attribution", unit=" roles", colour="#2c8558"):
            role_name = r_metadata.get('name')
            teams = r_metadata.get('teams')
            role_id = role_lookup.get(role_name)
            group_id_list = []
            for team in teams:
                group_id = group_lookup.get(team)
                group_id_list.append(group_id)
            self.set_role(role_id=role_id, group_id=group_id_list)

    def sync_roles(self):
        all_role_lookup = self.create_allrole_lookup()
        all_role_lookup.pop('Admin')
        yaml_role = [role.get('name') for role in self.role_metadata]

        for role_name in all_role_lookup.keys():
            if role_name not in yaml_role:
                role_id = all_role_lookup.get(role_name)
                self.sdk.delete_role(role_id=role_id)

    def execute(self):
        created_roles = self.create_instance_roles()
        self.attribute_instance_roles(created_role_metadata=created_roles)
        self.sync_roles()
