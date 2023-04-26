from tqdm import tqdm
import logging
from lmanage.utils.errorhandling import return_sleep_message
from lmanage.utils.looker_object_constructors import DashboardObject
import coloredlogs
from yaspin import yaspin

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')
logging.getLogger("looker_sdk").setLevel(logging.WARNING)

class CaptureDashboards():
    def __init__(self, sdk, folder_root: dict):
        self.sdk = sdk
        self.folder_root = folder_root

    def get_all_dashboards(self) -> dict:
        system_folders = ['Users','Embed Users','Embed Groups', 'LookML Dashboards']
        scrub_dashboards = {}
        with yaspin().white.bold.shark.on_blue as sp:
            sp.text="getting all system dashboard metadata (can take a while)"
            all_dashboards = self.sdk.all_dashboards(fields="id,folder")
        
        for dash in all_dashboards:
            if dash.folder.id == 'lookml':
                continue
            else:
                folder_root = self.folder_root.get(dash.folder.id, [{'name':'Users'}])[0]['name']
                if dash.folder.id in list(self.folder_root.keys()) and folder_root not in system_folders:
                    scrub_dashboards[dash.id] = dash.folder.id 
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