import looker_sdk
from tqdm import tqdm
from looker_sdk import models40 as models
import yaml 
from lmanage.utils.looker_object_constructors import DashboardObject
from lmanage.utils.errorhandling import return_sleep_message


class Create_Dashboards():

    def __init__(self, sdk, folder_mapping, content_metadata) -> None:
        self.sdk = sdk
        self.folder_mapping = folder_mapping
        self.content_metadata = content_metadata
    
    def upload_dashboards(self) -> None:
        for dash in tqdm(self.content_metadata, desc = "Dashboard Upload", unit="dashboards", colour="#2c8558"):
            t = dash.get('legacy_folder_id')
            new_folder_id = self.folder_mapping.get(t)
            new_folder_id = new_folder_id if new_folder_id != 'Shared' else 1 
            body = models.WriteDashboardLookml(
                folder_id=new_folder_id, 
                lookml=dash['lookml']
            )
            # lookml = self.amend_lookml_str(dash['lookml'])
            self.sdk.import_dashboard_from_lookml(body=body)

    def execute(self):
        self.upload_dashboards()