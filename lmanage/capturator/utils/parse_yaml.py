import json
import yaml
import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')


class Yaml:
    def __init__(self, yaml_path):
        self.yaml_path = yaml_path
        with open(self.yaml_path, 'r') as file:
            self.parsed_yaml = yaml.load(file, Loader=yaml.BaseLoader)

    def get_permission_metadata(self):
        if 'permission_sets' in self.parsed_yaml:
            return self.parsed_yaml.get('permission_sets')
        return None

    def get_model_set_metadata(self):
        if 'model_sets' in self.parsed_yaml:
            return self.parsed_yaml.get('model_sets')
        return None

    def get_role_metadata(self):
        if 'roles' in self.parsed_yaml:
            return self.parsed_yaml.get('roles')
        return None

    def get_folder_metadata(self):
        if 'folder_permissions' in self.parsed_yaml:
            return self.parsed_yaml.get('folder_permissions')
        return None

    def get_user_attribute_metadata(self):
        if 'user_attributes' in self.parsed_yaml:
            return self.parsed_yaml.get('user_attributes')
        return None
