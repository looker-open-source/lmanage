import logging
import coloredlogs
from looker_sdk import models, error

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


class CreateAndAssignUserAttributes():
    def __init__(self, user_attributes, sdk):
        self.user_attribute_metadata = user_attributes
        self.sdk = sdk

    def existing_user_attributes(self) -> dict:
        all_instance_ua = self.sdk.all_user_attributes()

        all_ua = {ua.name: ua.id for ua in all_instance_ua}
        return all_ua

    def create_user_attribute_if_not_exists(self):
        existing_ua = self.existing_user_attributes()
        yaml_user_attributes = self.user_attribute_metadata

        for ua in yaml_user_attributes:
            name = ua.get('name')
            if name in existing_ua.keys():
                logger.warn(
                    f'user attribute {name} already exists on this instance')
            else:
                datatype = ua.get('uatype')
                value_is_hidden = ua.get('hidden_value')
                user_view = ua.get('user_view')
                user_edit = ua.get('user_edit')

                ua_permissions = models.WriteUserAttribute(
                    name=name,
                    label=name,
                    type=datatype,
                    value_is_hidden=value_is_hidden,
                    user_can_view=user_view,
                    user_can_edit=user_edit,
                    default_value=ua.get('default_value')
                )

                response = self.sdk.create_user_attribute(body=ua_permissions)
                logger.info(f'created user attribute {response.label}')

    def sync_user_attributes(self):
        instance_ua = self.existing_user_attributes()
        config_ua = [ua.get('name') for ua in self.user_attribute_metadata]
        sys_default_ua = [
            'email',
            'first_name',
            'id',
            'landing_page',
            'last_name',
            'number_format',
            'locale',
            'name'
        ]

        for ua in sys_default_ua:
            if ua in instance_ua:
                instance_ua.pop(ua, None)

        for ua_name in instance_ua.keys():
            if ua_name not in config_ua:
                ua_id = instance_ua.get(ua_name)
                self.sdk.delete_user_attribute(ua_id)
                logger.info(
                    f'''deleting ua {ua_name} because
                    it is not listed in the yaml config''')

    def add_group_values_to_ua(self):
        instance_ua = self.existing_user_attributes()
        all_instance_groups = self.sdk.all_groups()
        group_metadata = {
            group.name: group.id for group in all_instance_groups}
        yaml_user_attributes = self.user_attribute_metadata
        for ua in yaml_user_attributes:
            if len(ua.get('teams')) > 0:
                for team_val in ua.get('teams'):
                    group_id = group_metadata.get(list(team_val.keys())[0])

                    meta_value = list(team_val.values())[0]
                    ua_id = instance_ua.get(ua.get('name'))

                    params_to_add = models.UserAttributeGroupValue(
                        value=meta_value,
                        value_is_hidden=False
                    )

                    self.sdk.update_user_attribute_group_value(
                        group_id=group_id,
                        user_attribute_id=ua_id,
                        body=params_to_add)

    def execute(self):
        # CREATE NEW USER ATTRIBUTES
        self.create_user_attribute_if_not_exists()

        # DELETE ALL USER ATTRIBUTES THAT DON'T MATCH WITH YAML
        self.sync_user_attributes()

        # ADD VALUES TO INSCOPE USER ATTRIBUTES
        self.add_group_values_to_ua()
