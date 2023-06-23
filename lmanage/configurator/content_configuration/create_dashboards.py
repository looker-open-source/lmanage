from tqdm import tqdm
from looker_sdk import models40 as models
from lmanage.utils import logger_creation as log_color

#logger = log_color.init_logger(__name__, logger_level)


class Create_Dashboards():
    def __init__(self, sdk, folder_mapping, content_metadata, logger) -> None:
        self.sdk = sdk
        self.folder_mapping = folder_mapping
        self.content_metadata = content_metadata
        self.logger = logger

    
    def upload_dashboards(self) -> None:
        resp = []
        for dash in tqdm(self.content_metadata, desc = "Dashboard Upload", unit="dashboards", colour="#2c8558"):
            self.logger.debug(type(dash))
            t = dash.get('legacy_folder_id').get('folder_id')
            new_folder_id = self.folder_mapping.get(t)
            new_folder_id = new_folder_id if new_folder_id != 'Shared' else 1 
            body = models.WriteDashboardLookml(
                folder_id=new_folder_id, 
                lookml=dash['lookml']
            )
            # lookml = self.amend_lookml_str(dash['lookml'])
            temp = {}
            new_dash = self.sdk.import_dashboard_from_lookml(body=body)
            temp[dash['dashboard_id']] = new_dash.id 
            resp.append(temp)
        return resp


    def execute(self):
        mapping = self.upload_dashboards()
        self.logger.debug(mapping)
        return mapping