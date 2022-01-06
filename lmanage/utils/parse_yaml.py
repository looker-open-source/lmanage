import json
import yaml
import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')


class Yaml:
    def __init__(self, yaml_path):
        self.yaml_path = yaml_path

    def read_provision_yaml(self) -> json:
        """ Load YAML configuration file to a dictionary
        """
        with open(self.yaml_path, 'r') as file:
            parsed_yaml = yaml.safe_load(file)
            logger.debug(parsed_yaml)
            return parsed_yaml


# x = Yaml(yaml_path='/usr/local/google/home/hugoselbie/code_sample/py/clients/snap/okta_groups/snap_group_mapping.yaml')
# print(x.read_provision_yaml())
