from lmanage.utils import parse_yaml as py, logger_creation as log_color


class LookerConfigReader():
    def __init__(self, config_dir):
        logger_level = 'INFO'  # kwargs.get('verbose')
        logger = log_color.init_logger(__name__, logger_level)
        logger.info(
            '----------------------------------------------------------------------------------------')
        logger.info('parsing yaml file')
        self.settings_yaml = py.Yaml(yaml_path=f'{config_dir}/settings.yaml')
        self.content_yaml = py.Yaml(yaml_path=f'{config_dir}/content.yaml')
        # self.logger = log_color.init_logger(__name__, logger_level)

    def read(self):
        return {
            'folder_metadata': self.settings_yaml.get_metadata('folder_metadata'),
            'permission_set_metadata': self.settings_yaml.get_metadata('permission_set_metadata'),
            'model_set_metadata': self.settings_yaml.get_metadata('model_set_metadata'),
            'role_metadata': self.settings_yaml.get_metadata('role_metadata'),
            'user_attribute_metadata': self.settings_yaml.get_metadata('user_attribute_metadata'),
            'look_metadata': self.content_yaml.get_metadata('look_metadata'),
            'dashboard_metadata': self.content_yaml.get_metadata('dashboard_metadata'),
            #     'board_metadata': self.content_yaml.get_metadata('board_metadata'),
        }
