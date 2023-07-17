import looker_sdk
import ruamel.yaml
import os
from lmanage.looker_config import LookerConfig
from lmanage.logger_config import setup_logger
from looker_sdk import error
from lmanage.utils import looker_object_constructors as loc, errorhandling as eh

logger = setup_logger()


class LookerConfigSaver():
    def __init__(self, export_dir):
        self.__init_yaml()
        self.export_dir = export_dir
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

    def save(self, config: LookerConfig):
        self.__save_settings(config.settings)
        self.__save_content(config.content)

    def __save_settings(self, settings):
        # Folder Permissions
        with open(f'{self.export_dir}/settings.yaml', 'w') as file:
            fd_yml_txt = '''# FOLDER_PERMISSIONS\n# Opening Session Welcome to the Capturator, this is the Folder place\n# -----------------------------------------------------\n\n'''
            file.write(fd_yml_txt)
            self.yaml.dump(settings['folder_permissions'], file)

        # Roles, Permission Sets & Model Sets
        with open(f'{self.export_dir}/settings.yaml', 'a') as file:
            r_yml_txt = '''# Looker Role\n# Opening Session Welcome to the Capturator, this is the Role place\n# -----------------------------------------------------\n\n'''
            file.write(r_yml_txt)
            file.write('\n\n# PERMISSION SETS\n')
            self.yaml.dump(settings['permission_sets'], file)
            file.write('\n\n# MODEL SETS\n')
            self.yaml.dump(settings['model_sets'], file)
            file.write('\n\n# LOOKER ROLES\n')
            self.yaml.dump(settings['roles'], file)

        # User Attributes
        with open(f'{self.export_dir}/settings.yaml', 'a') as file:
            file.write('\n\n# USER_ATTRIBUTES\n')
            self.yaml.dump(settings['user_attributes'], file)

    def __save_content(self, content):
        # Boards
        # with open(f'{self.export_dir}/content.yaml', 'w+') as file:
        #     file.write('\n\n# BoardData\n')
        #     self.yaml.dump(self.content.boards, file)

        # Looks
        looks = content['looks']
        with open(f'{self.export_dir}/content.yaml', 'wb') as file:
            file.write(bytes('\n\n# LookData\n', 'utf-8'))
            if eh.test_object_data(looks):
                self.yaml.dump(looks, file)
            else:
                file.write(bytes('#No Captured Looks', 'utf-8'))

        # Dashboards
        dashboards = content['dashboards']
        with open(f'{self.export_dir}/content.yaml', 'ab') as file:
            file.write(bytes('\n\n# Dashboard Content\n', 'utf-8'))
            if eh.test_object_data(dashboards):
                self.yaml.dump(dashboards, file)
            else:
                file.write(bytes('#No Captured Dashboards', 'utf-8'))

    def __init_yaml(self):
        self.yaml = ruamel.yaml.YAML()
        self.yaml.register_class(loc.LookerFolder)
        self.yaml.register_class(loc.LookerModelSet)
        self.yaml.register_class(loc.LookerPermissionSet)
        self.yaml.register_class(loc.LookerRoles)
        self.yaml.register_class(loc.LookerUserAttribute)
        self.yaml.register_class(loc.LookObject)
        self.yaml.register_class(loc.DashboardObject)
        self.yaml.register_class(loc.BoardObject)
        self.yaml.register_class(looker_sdk.sdk.api40.models.ScheduledPlan)
        self.yaml.register_class(
            looker_sdk.sdk.api40.models.ScheduledPlanDestination)
        self.yaml.register_class(looker_sdk.sdk.api40.models.UserPublic)
