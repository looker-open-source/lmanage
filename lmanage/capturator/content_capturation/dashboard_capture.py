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

    def __init__(self, sdk):
        self.sdk = sdk

    def get_all_dashboards(self) -> dict:
        system_folders = ['Users','Embed Users','Embed Groups']
        scrub_dashboards = {}
        with yaspin().white.bold.shark.on_blue as sp:
            sp.text="getting all system look metadata (can take a while)"
            all_dashboards = self.sdk.all_dashboards(fields="id,folder")
            folder_length = len(all_dashboards)
        
        folder_history = {}
        l =0
        for dash in all_dashboards:
            l +=1
            if dash.folder.id in list(folder_history.keys()):
                folder_root = folder_history.get(dash.folder.id)
            else:
                folder_root = None
                trys = 0
                while folder_root is None:
                    trys += 1
                    try:
                        with yaspin().white.bold.shark.on_blue as sp:
                            sp.text=f"getting folder ancestors for folder {l} / {folder_length}"
                            folder_root = self.sdk.folder_ancestors(folder_id=dash.folder.id, fields="name") 
                    except:
                        return_sleep_message(call_number=trys, quiet=False)
                folder_history[dash.folder.id] = folder_root
            
            if folder_root:
                if folder_root[0].id not in system_folders:
                    scrub_dashboards[dash.id] = dash.folder.id
            else:
                continue
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