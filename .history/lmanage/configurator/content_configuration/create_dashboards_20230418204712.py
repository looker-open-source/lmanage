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
    
    def amend_lookml_str(self, lookml: str) -> str:
        y = lookml.replace("\\'","'")
        z = y.replace('"', '\"')
        return z


    def upload_dashboards(self) -> None:
        for dash in tqdm(self.content_metadata, desc = "Dashboard Upload", unit="dashboards", colour="#2c8558"):
            t = dash.get('legacy_folder_id')
            new_folder_id = self.folder_mapping.get(t)

            lookml = self.amend_lookml_str(lookml=dash['lookml'])
            
            # lookml = self.amend_lookml_str(dash['lookml'])
            self.sdk.import_dashboard_from_lookml(body=models.WriteDashboardLookml(
                folder_id = new_folder_id,
                lookml = lookml))

    def execute(self):
        self.upload_dashboards()