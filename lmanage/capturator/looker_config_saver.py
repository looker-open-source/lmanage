import looker_sdk
import ruamel.yaml
import os
from lmanage.looker_config import LookerConfig
from lmanage.logger_config import setup_logger
from lmanage.utils import looker_object_constructors as loc, errorhandling as eh

logger = setup_logger()


class LookerConfigSaver():
    def __init__(self, config_dir):
        self.__init_yaml()
        self.config_dir = config_dir
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

    def save(self, config: LookerConfig):
        self.__save_settings(config.settings)
        self.__save_content(config.content)

    def __init_yaml(self):
        self.yaml = ruamel.yaml.YAML()
        self.yaml.register_class(loc.LookerFolder)
        self.yaml.register_class(loc.LookerModelSet)
        self.yaml.register_class(loc.LookerPermissionSet)
        self.yaml.register_class(loc.LookerRoles)
        self.yaml.register_class(loc.LookerUserAttribute)
        self.yaml.register_class(loc.LookObject)
        self.yaml.register_class(loc.DashboardObject)
        self.yaml.register_class(loc.AlertObject)
        self.yaml.register_class(loc.AlertAppliedDashboardFilterObject)
        self.yaml.register_class(loc.AlertDestinationObject)
        self.yaml.register_class(loc.AlertFieldObject)
        self.yaml.register_class(loc.AlertFieldFilterObject)
        self.yaml.register_class(loc.BoardObject)
        self.yaml.register_class(looker_sdk.sdk.api40.models.ScheduledPlan)
        self.yaml.register_class(
            looker_sdk.sdk.api40.models.ScheduledPlanDestination)
        self.yaml.register_class(looker_sdk.sdk.api40.models.UserPublic)

    def __save_settings(self, settings):
        # Folder Permissions
        with open(self.__get_settings_path(), 'w') as file:
            fd_yml_txt = '''# FOLDER_PERMISSIONS\n# Opening Session Welcome to the Capturator, this is the Folder place\n# -----------------------------------------------------\n\n'''
            file.write(fd_yml_txt)
            self.yaml.dump(settings['folder_permissions'], file)

        # Roles, Permission Sets & Model Sets
        with open(self.__get_settings_path(), 'a') as file:
            r_yml_txt = '''# Looker Role\n# Opening Session Welcome to the Capturator, this is the Role place\n# -----------------------------------------------------\n\n'''
            file.write(r_yml_txt)
            file.write('\n\n# PERMISSION SETS\n')
            self.yaml.dump(settings['permission_sets'], file)
            file.write('\n\n# MODEL SETS\n')
            self.yaml.dump(settings['model_sets'], file)
            file.write('\n\n# LOOKER ROLES\n')
            self.yaml.dump(settings['roles'], file)

        # User Attributes
        with open(self.__get_settings_path(), 'a') as file:
            file.write('\n\n# USER_ATTRIBUTES\n')
            self.yaml.dump(settings['user_attributes'], file)

    def __save_content(self, content):
        # Boards
        # with open(self.__get_content_path(), 'w+') as file:
        #     file.write('\n\n# BoardData\n')
        #     self.yaml.dump(self.content.boards, file)

        # Looks
        looks = content['looks']
        with open(self.__get_content_path(), 'wb') as file:
            file.write(bytes('\n\n# LookData\n', 'utf-8'))
            if eh.test_object_data(looks):
                self.yaml.dump(looks, file)
            else:
                file.write(bytes('#No Captured Looks', 'utf-8'))

        # Dashboards
        dashboards = content['dashboards']
        with open(self.__get_content_path(), 'ab') as file:
            file.write(bytes('\n\n# Dashboard Content\n', 'utf-8'))
            if eh.test_object_data(dashboards):
                self.yaml.dump(dashboards, file)
            else:
                file.write(bytes('#No Captured Dashboards', 'utf-8'))

    def __get_settings_path(self):
        return f'{self.config_dir}/settings.yaml'

    def __get_content_path(self):
        return f'{self.config_dir}/content.yaml'
