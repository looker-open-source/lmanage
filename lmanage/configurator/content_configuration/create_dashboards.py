import looker_sdk
from looker_sdk import models40 as models
from ruamel.yaml import YAML
from lmanage.utils.looker_object_constructors import DashboardObject
from lmanage.utils.errorhandling import return_sleep_message


class create_Dashboards():

    def __init__(self, sdk, folder_mapping, content_metadata) -> None:
        self.sdk = sdk
        self.folder_mapping = folder_mapping
        self.content_metadata = content_metadata
        self.yaml_path = "output/demo_dashboard_output"

    def get_dashboard_file(self) -> list:
        f = open(f'{self.yaml_path}.yaml', 'r')
        yaml=YAML(typ="safe")
        yaml.register_class(DashboardObject)
        dash_data = yaml.load(f)
        return dash_data
        

    def process_dashboard_file() -> list:
        pass

    def upload_dashboards(self, dash_data) -> None:
        for dash in dash_data:
            self.sdk.import_dashboard_from_lookml(body=models.WriteDashboardLookml(
                folder_id = dash.legacy_folder_id,
                lookml = dash.lookml))

    def execute(self):
        dash_data = self.get_dashboard_file()
        self.upload_dashboards(dash_data)

ini = "/usr/local/google/home/belvederej/Code/ini_files/joe.ini"
sdk = looker_sdk.init40(config_file=ini)
test = create_Dashboards(sdk,"","")
test.execute()