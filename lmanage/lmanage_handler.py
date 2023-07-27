from lmanage.capturator.looker_api_reader import LookerApiReader
from lmanage.capturator.looker_config_saver import LookerConfigSaver
from lmanage.configurator.looker_config_reader import LookerConfigReader


class LManageConfig():
    def __init__(self, settings, content):
        self.settings = settings
        self.content = content


class LManageHandler():
    def __init__(self, ini_file: str, config_dir: str, verbose_logs: bool = None):
        self.ini_file = ini_file
        self.config_dir = config_dir
        self.verbose_logs = verbose_logs

    def capture(self):
        reader = LookerApiReader(self.ini_file)
        saver = LookerConfigSaver(self.config_dir)
        config = reader.get_config()
        saver.save(config)

    def configure(self):
        print('')
        # reader = LookerConfigReader(self.config_dir)
        # config = reader.read()
        # saver.save(config)


# if __name__ == "__main__":
#     instance = 'dev'
#     IP = (
#         f'/usr/local/google/home/hugoselbie/code_sample/py/ini/{instance}.ini')
#     YP = (
#         f'/usr/local/google/home/hugoselbie/code_sample/py/lmanage/tests/example_yamls/{instance}_output.yaml')

#     main(yaml_export_path=YP, ini_file=IP)
