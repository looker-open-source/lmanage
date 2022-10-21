import logging
import coloredlogs
from looker_sdk import models, error

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


class ExtractUserAttributes():
    def __init__(self,  sdk):
        self.sdk = sdk

    def existing_user_attributes(self) -> dict:
        all_instance_ua = self.sdk.all_user_attributes()

        return all_instance_ua

    def group_values_to_ua(self, user_attribute_metadata):

        all_instance_groups = self.sdk.all_groups()
        group_metadata = {
            group.id: group.name for group in all_instance_groups}
        response = {}
        for ua in user_attribute_metadata:
            group_assign = self.sdk.all_user_attribute_group_values(
                user_attribute_id=ua.id)
            teams = []
            values = []
            response[ua.name] = {}
            response[ua.name]['type'] = ua.type
            response[ua.name]['hidden_value'] = ua.value_is_hidden
            response[ua.name]['user_view'] = ua.user_can_view
            response[ua.name]['user_edit'] = ua.user_can_edit
            # response[ua.name]['value'] = ua.values

            for group in group_assign:
                group_name = group_metadata.get(group.group_id)
                teams.append(group_name)
                if group.value not in values:
                    values.append(group.value)
                else:
                    pass

            response[ua.name]['teams'] = teams
            response[ua.name]['value'] = values

        return {'user_attributes': response}

    def execute(self):
        ua_metadata_ = self.existing_user_attributes()

        something = self.group_values_to_ua(
            user_attribute_metadata=ua_metadata_)

        return something
