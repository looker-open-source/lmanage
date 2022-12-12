import logging
import coloredlogs
from time import sleep
from lmanage.utils.errorhandling import return_error_message, return_sleep_message

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


class LookerUserAttribute():
    def __init__(self, teams_val: dict, name: str, uatype: bool, hidden_value: bool, user_view, user_edit, default_value) -> object:
        self.name = name
        self.uatype = uatype
        self.hidden_value = hidden_value
        self.user_view = str(user_view)
        self.user_edit = str(user_edit)
        self.default_value = default_value
        self.teams = teams_val


class ExtractUserAttributes():
    def __init__(self,  sdk):
        self.sdk = sdk
        self.user_attribute_metadata = self.existing_user_attributes()
        self.all_group_metadata = self.all_group_metadatas()

    def existing_user_attributes(self) -> dict:
        ex_ua = None
        while ex_ua is None:
            try:
                ex_ua = self.sdk.all_user_attributes()
            except:
                return_sleep_message()
        for ua in enumerate(ex_ua):
            if ua[1].get('is_system'):
                ua_idx = ua[0]
                ex_ua.pop(ua_idx)
        return ex_ua

    def all_group_metadatas(self):
        return self.sdk.all_groups()

    def create_user_attributes(self):

        group_metadata = {
            group.id: group.name for group in self.all_group_metadata}
        response = []
        for ua in self.user_attribute_metadata:
            group_assign = None
            while group_assign is None:
                try:
                    group_assign = self.sdk.all_user_attribute_group_values(
                        user_attribute_id=ua.id)
                    # logger.info(
                    #     'capturing groups associated with user attribute %s', group_assign[0].get('user_attribute_id'))
                except:
                    return_sleep_message()
            team_values = []

            for group in group_assign:
                group_name = group_metadata.get(group.group_id)
                teams = {}
                teams[group_name] = group.value
                team_values.append(teams)
            looker_ua = LookerUserAttribute(
                name=ua.name,
                uatype=ua.type,
                hidden_value=ua.value_is_hidden,
                user_view=ua.user_can_view,
                user_edit=ua.user_can_edit,
                default_value=ua.default_value,
                teams_val=team_values
            )
            response.append(looker_ua)
        return response
