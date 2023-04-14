import looker_sdk
from tqdm import tqdm
from looker_sdk import models40 as models
from ruamel.yaml import YAML
from lmanage.utils.looker_object_constructors import DashboardObject
from lmanage.utils.errorhandling import return_sleep_message


class Create_Dashboards():

    def __init__(self, sdk, folder_mapping, content_metadata) -> None:
        self.sdk = sdk
        self.folder_mapping = folder_mapping
        self.content_metadata = content_metadata

    def upload_dashboards(self) -> None:
        for dash in tqdm(self.content_metadata, desc = "Dashboard Upload", unit=" dashboards", colour="#2c8558"):
            new_folder_id = self.folder_mapping[dash['legacy_folder_id']]
            self.sdk.import_dashboard_from_lookml(body=models.WriteDashboardLookml(
                folder_id = new_folder_id,
                lookml = dash['lookml']))

    def execute(self):
        self.upload_dashboards()