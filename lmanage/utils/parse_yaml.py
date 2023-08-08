import json
import ruamel.yaml as yaml
import logging
from lmanage.utils import logger_creation as log_color


class Yaml:
    def __init__(self, yaml_path):
        self.yaml_path = yaml_path
        with open(self.yaml_path, 'r') as file:
            self.parsed_yaml = yaml.load(file, Loader=yaml.BaseLoader)

    def get_metadata(self, type):
        if type == 'folder_metadata':
            metadata = self.__get_folder_metadata()
        elif type == 'permission_set_metadata':
            metadata = self.__get_permission_metadata()
        elif type == 'model_set_metadata':
            metadata = self.__get_model_set_metadata()
        elif type == 'role_metadata':
            metadata = self.__get_role_metadata()
        elif type == 'user_attribute_metadata':
            metadata = self.__get_user_attribute_metadata()
        elif type == 'look_metadata':
            metadata = self.__get_look_metadata()
        elif type == 'dashboard_metadata':
            metadata = self.__get_dashboard_metadata()
        elif type == 'board_metadata':
            metadata = self.__get_board_metadata()

        if not metadata:
            print('')
            # log f'No {type} specified. Please check your yaml file at {self.yaml_path}.')

        return metadata

    def __get_permission_metadata(self):
        response = []
        for objects in self.parsed_yaml:
            if 'permissions' in list(objects.keys()):
                response.append(objects)
        response = [r for r in response if r.get('name') != 'Admin']
        return response

    def __get_model_set_metadata(self):
        response = []
        for objects in self.parsed_yaml:
            if 'models' in list(objects.keys()):
                response.append(objects)
        return response

    def __get_role_metadata(self):
        response = []
        for objects in self.parsed_yaml:
            if 'permission_set' and 'model_set' in list(objects.keys()):
                response.append(objects)
        response = [r for r in response if r.get('name') != 'Admin']
        return response

    def __get_folder_metadata(self):
        response = []
        for objects in self.parsed_yaml:
            if 'content_metadata_id' in list(objects.keys()):
                response.append(objects)
        return response

    def __get_user_attribute_metadata(self):
        response = []
        for objects in self.parsed_yaml:
            if 'hidden_value' in list(objects.keys()):
                response.append(objects)
        return response

    def __get_look_metadata(self):
        response = []
        for objects in self.parsed_yaml:
            if 'query_obj' in list(objects.keys()):
                response.append(objects)
        return response

    def __get_dashboard_metadata(self):
        response = []
        for objects in self.parsed_yaml:
            if 'lookml' in list(objects.keys()):
                response.append(objects)
        return response

    def __get_board_metadata(self):
        response = []
        for objects in self.parsed_yaml:
            if 'board_sections' in list(objects.keys()):
                response.append(objects)
        return response
