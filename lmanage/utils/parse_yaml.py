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
        response = []
        for objects in self.parsed_yaml:
            if 'permissions' in list(objects.keys()):
                response.append(objects)
        response = [r for r in response if r.get('name') != 'Admin']
        return response

    def get_model_set_metadata(self):
        response = []
        for objects in self.parsed_yaml:
            if 'models' in list(objects.keys()):
                response.append(objects)
        return response

    def get_role_metadata(self):
        response = []
        for objects in self.parsed_yaml:
            if 'permission_set' and 'model_set' in list(objects.keys()):
                response.append(objects)
        response = [r for r in response if r.get('name') != 'Admin']
        return response

    def get_folder_metadata(self):
        response = []
        for objects in self.parsed_yaml:
            if 'content_metadata_id' in list(objects.keys()):
                response.append(objects)
        return response

    def get_user_attribute_metadata(self):
        response = []
        for objects in self.parsed_yaml:
            if 'hidden_value' in list(objects.keys()):
                response.append(objects)
        return response
