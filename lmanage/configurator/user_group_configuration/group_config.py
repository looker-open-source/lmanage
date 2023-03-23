import logging
import coloredlogs
from looker_sdk import models, error
from lmanage.utils.errorhandling import return_error_message

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


class CreateInstanceGroups():
    def __init__(self, folders, user_attributes, roles, sdk) -> None:
        self.folder_metadata = folders
        self.user_attribute_metadata = user_attributes
        self.role_metadata = roles
        self.sdk = sdk

    def extract_teams(self, container, data_storage, ua: bool):
        for team in container:
            team_list = team.get('teams')
            if len(team_list) > 0:
                if ua:
                    for team_val in team_list:
                        team_app = list(team_val.keys())[0]
                        data_storage.append(team_app)
                else:
                    for team_val in team_list:
                        data_storage.append(team_val)
        return data_storage

    def extract_folder_teams(self, container, data_storage):
        for folder_element in container:
            for folder in folder_element:
                if isinstance(folder.get('team_edit'), list):
                    edit_group = folder.get('team_edit')
                    for group in edit_group:
                        data_storage.append(group)
                if isinstance(folder.get('team_view'), list):
                    view_group = folder.get('team_view')
                    for group in view_group:
                        data_storage.append(group)
                else:
                    pass

    def create_group_if_not_exists(self,
                                   sdk,
                                   group_name: str) -> dict:
        """ Create a Looker Group and add Group attributes

        :group_name: Name of a Looker group to create.
        :rtype: Looker Group object.
        """
        # get group if exists
        try:
            logger.info(f'Creating group "{group_name}"')
            group = sdk.create_group(
                body=models.WriteGroup(
                    can_add_to_content_metadata=True,
                    name=group_name
                )
            )
            return group
        except error.SDKError as grouperr:
            err_msg = return_error_message(grouperr)
            logger.warn(
                'You have hit a warning creating your group; warning = %s', err_msg)
            logger.debug(grouperr)
            group = sdk.search_groups(name=group_name)
            return group[0]

    def get_instance_group_metadata(self,
                                    sdk,
                                    unique_group_list: list) -> list:
        group_metadata = []

        for group_name in unique_group_list:
            group = self.create_group_if_not_exists(sdk, group_name)
            temp = {}
            temp['group_id'] = group.id
            temp['group_name'] = group.name
            group_metadata.append(temp)

        return group_metadata

    def sync_groups(self,
                    group_name_list: list) -> str:

        all_groups = self.sdk.all_groups()
        group_dict = {group.name: group.id for group in all_groups}
        # Deleting Standard Groups
        del group_dict['All Users']

        for group_name in group_dict.keys():
            if group_name not in group_name_list:
                self.sdk.delete_group(group_id=group_dict[group_name])
                logger.info(
                    f'deleting group {group_name} to sync with yaml config')

        return 'your groups are in sync with your yaml file'

    def execute(self):
        team_list = []
        # extracting user attribute teams
        self.extract_teams(container=self.user_attribute_metadata,
                           data_storage=team_list, ua=True)
        # extracting role based teams
        self.extract_teams(
            container=self.role_metadata, data_storage=team_list, ua=False)
        # extract nested folder access teams
        self.extract_folder_teams(
            container=self.folder_metadata, data_storage=team_list)

        team_list = list(set(team_list))

        # create all the groups
        self.get_instance_group_metadata(
            sdk=self.sdk, unique_group_list=team_list)
        self.sync_groups(group_name_list=team_list)
