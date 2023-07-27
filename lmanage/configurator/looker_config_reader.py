from lmanage.utils import parse_yaml as py, errorhandling as eh, logger_creation as log_color


class LookerConfigReader():
    def __init__(self, config_dir):
        print('')
        # logger_level = kwargs.get('verbose')
        # logger = log_color.init_logger(__name__, logger_level)
        # logger.info(div)
        # logger.info('parsing yaml file')
        settings_yaml = py.Yaml(yaml_path=f'{config_dir}/settings.yaml')
        content_yaml = py.Yaml(yaml_path=f'{config_dir}/content.yaml')
        logger_level = 'INFO'  # kwargs.get('verbose')
        self.logger = log_color.init_logger(__name__, logger_level)

    def read(self):
        folder_metadata = __get_item(
            self.settings_yaml.get_folder_metadata())

        # permission_set_metadata = settings_yaml.get_permission_metadata()
        # if not permission_set_metadata:
        #     logger.warn(
        #         f'no permission_set_metadata specified please check your yaml file at {yaml_path}/settings.yaml')
        # model_set_metadata = settings_yaml.get_model_set_metadata()
        # if not model_set_metadata:
        #     logger.warn(
        #         f'no model_set_metadata specified please check your yaml file at {yaml_path}/settings.yaml')
        # role_metadata = settings_yaml.get_role_metadata()
        # if not role_metadata:
        #     logger.warn(
        #         f'no role_metadata specified please check your yaml file at {yaml_path}/settings.yaml')
        # user_attribute_metadata = settings_yaml.get_user_attribute_metadata()
        # if not user_attribute_metadata:
        #     logger.warn(
        #         f'no user_attribute_metadata specified please check your yaml file at {yaml_path}/settings.yaml')

        # look_metadata = content_yaml.get_look_metadata()
        # if not look_metadata:
        #     logger.warn(
        #         f'no look_metadata specified please check your yaml file at {yaml_path}/content.yaml')

        # dash_metadata = content_yaml.get_dash_metadata()
        # if not dash_metadata:
        #     logger.warn(
        #         f'no dash_metadata specified please check your yaml file at {yaml_path}/content.yaml')

        # board_metadata = content_yaml.get_board_metadata()
        # if not board_metadata:
        #     logger.warn(
        #         f'no board_metadata specified please check your yaml file at {yaml_path}/content.yaml')


def __get_item(self, item):
    if not item:
        self.logger.warn(
            f'no folder_metadata specified please check your yaml file at {self.config_path}/settings.yaml')
    return item
