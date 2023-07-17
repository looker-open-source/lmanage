# import logging
from lmanage.looker_config_reader import LookerConfigReader
from lmanage.looker_config_saver import LookerConfigSaver


class LookerConfigHandler():
    def __init__(self, **kwargs):
        self.ini_file = kwargs.get('ini_file')
        self.export_dir = kwargs.get('yaml_export_dir').rstrip('/')

    def handle(self):
        reader = LookerConfigReader(self.ini_file)
        config = reader.read()
        LookerConfigSaver(self.export_dir).save(config)


# if __name__ == "__main__":
#     instance = 'dev'
#     IP = (
#         f'/usr/local/google/home/hugoselbie/code_sample/py/ini/{instance}.ini')
#     YP = (
#         f'/usr/local/google/home/hugoselbie/code_sample/py/lmanage/tests/example_yamls/{instance}_output.yaml')

#     main(yaml_export_path=YP, ini_file=IP)
