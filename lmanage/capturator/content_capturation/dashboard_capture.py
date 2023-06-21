from tqdm import tqdm
import logging
from lmanage.utils import looker_object_constructors as loc, errorhandling as eh, logger_creation as log_color
from yaspin import yaspin

#logger = log_color.init_logger(__name__, logger_level)

class CaptureDashboards():
    def __init__(self, sdk, folder_root: dict, logger):
        self.sdk = sdk
        self.folder_root = folder_root
        self.logger = logger

    def get_all_dashboards(self) -> dict:
        scrub_dashboards = {}
        with yaspin().white.bold.shark.on_blue as sp:
            sp.text="getting all system dashboard metadata (can take a while)"
            all_dashboards = self.sdk.all_dashboards(fields="id,folder, slug")
        
        for dash in all_dashboards:
            if dash.folder.id in self.folder_root:
                scrub_dashboards[dash.id] = {}
                scrub_dashboards[dash.id]['folder_id'] = dash.folder.id
                scrub_dashboards[dash.id]['slug'] = dash.slug 
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
                schedule_plans = self.sdk.scheduled_plans_for_dashboard(dashboard_id=dash_id, all_users=True)
                while lookml is None:
                    trys += 1
                    try:
                        lookml = self.sdk.dashboard_lookml(dashboard_id=dash_id)
                    except:
                        eh.return_sleep_message(call_number=trys, quiet=True)
                
                self.logger.debug(lookml.lookml)
                captured_dashboard = loc.DashboardObject(
                    legacy_folder_id=all_dashboards.get(dash_id),
                    lookml=lookml.lookml,
                    dashboard_id=dash_id,
                    dashboard_slug=all_dashboards.get(dash_id).get('slug'),
                    schedule_plans=schedule_plans
                    )
                response.append(captured_dashboard)
        return response

    def execute(self):
        all_dashboards = self.get_all_dashboards()
        captured_dash = self.get_dashboard_lookml(all_dashboards)
        return captured_dash