import looker_sdk
from tqdm import tqdm
from time import sleep
import logging
from lmanage.utils.errorhandling import return_sleep_message, calc_done_percent
from lmanage.utils.looker_object_constructors import DashboardObject


class CaptureDashboards():

    def __init__(self, sdk):
        self.sdk = sdk

    def get_all_dashboards(self) -> dict:
        all_dashboards = self.sdk.all_dashboards()
        scrub_dashboards = {dash.id: dash.folder.id for dash in all_dashboards if not dash.folder.is_personal or not dash.folder.is_embed}
        return scrub_dashboards

    def get_dashboard_lookml(self, all_dashboards: dict) -> list:
        #logging.info("Beginning Dashboard Capture:")
        response = []
  
        for dash_id in tqdm(all_dashboards, desc = "Dashboard Capture", unit=" dashboards", colour="#2c8558"):
        
            lookml = None
            trys = 0
            if "::" in dash_id:
                continue
            else:
                while lookml is None:
                    trys += 1
                    try:
                        lookml = self.sdk.dashboard_lookml(dashboard_id=dash_id)
                    except:
                        return_sleep_message(call_number=trys, quiet=True)

                captured_dashboard = DashboardObject(
                    legacy_folder_id=all_dashboards.get(dash_id),
                    lookml=lookml.lookml,
                    dashboard_id=dash_id)
                response.append(captured_dashboard)
            

        return response

    def execute(self):
        all_dashboards = self.get_all_dashboards()
        captured_dash = self.get_dashboard_lookml(all_dashboards)
        return captured_dash