import looker_sdk
from looker_sdk import models40 as models
from ruamel.yaml import YAML
from lmanage.utils.looker_object_constructors import DashboardObject
from lmanage.utils.errorhandling import return_sleep_message
from progress.bar import ChargingBar


class Create_Dashboards():

    def __init__(self, sdk, folder_mapping, content_metadata) -> None:
        self.sdk = sdk
        self.folder_mapping = folder_mapping
        self.content_metadata = content_metadata

    def upload_dashboards(self) -> None:
        bar = ChargingBar('Creating Dashboards', max=len(self.content_metadata))
        for dash in self.content_metadata:
            bar.next
            new_folder_id = self.folder_mapping.get(dash['legacy_folder_id'])
            response = self.sdk.import_dashboard_from_lookml(body=models.WriteDashboardLookml(
                folder_id = new_folder_id,
                lookml = dash['lookml']))
        bar.finish()

    def execute(self):
        self.upload_dashboards()