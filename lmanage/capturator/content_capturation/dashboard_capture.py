import looker_sdk
from tqdm import tqdm
from time import sleep
import logging
from lmanage.utils.errorhandling import return_sleep_message
from lmanage.utils.looker_object_constructors import DashboardObject

class CaptureDashboards():

    def __init__(self, sdk):
        self.sdk = sdk

    def get_all_dashboards(self):

        all_dashboards = None
        trys = 0
        while all_dashboards is None:
            trys += 1
            try:
                all_dashboards = self.sdk.all_dashboards(fields="id, folder")
            except:
                return_sleep_message(call_number=trys)

        return all_dashboards
    
    
    def get_dashboard_lookml(self, all_dashboards):
        
        logging.info("Beginning Dashboard Capture:")

        skippedDash = []
        for i in tqdm(range(len(all_dashboards))):
            dash = all_dashboards[i]
            lookml = None
            trys = 0
            skip = False

            while lookml is None:
                trys += 1
                try:
                    lookml = self.sdk.dashboard_lookml(dashboard_id=dash.id)
                except looker_sdk.error.SDKError as exc:
                    error_data = exc
                    if "Max retries exceeded with url" in error_data.message:
                        return_sleep_message(call_number=trys, quiet=True)
                    else:
                        skip = True
                        break

            if skip:
                skippedDash.append([i,dash.id,error_data.message])
            else:                        
                dash.lookml = lookml.lookml

        if len(skippedDash) != 0:
            all_dashboards = self.logAndRemoveSkippedDash(all_dashboards,skippedDash)

        return all_dashboards
    
    def create_Dashboard_obj(self, all_dashboards):
        dash_objs = []
        for dash in all_dashboards:
            dash_objs.append(DashboardObject(dash.folder.id,dash.lookml,dash.id))
        return dash_objs
    
    def logAndRemoveSkippedDash(self, all_dashboards, skippedDash) -> list:
        errorString = "The following dashboards were not logged: "
        skippedDash.reverse()
        for dash in skippedDash:
            errorString += '\n' + "ID: " + dash[1] + "\n Error: " + dash[2] + '\n'
            del all_dashboards[dash[0]]
        
        logging.error(errorString)
        return all_dashboards

    def execute(self):
        all_dashboards = self.get_all_dashboards()
        all_dashboards = self.get_dashboard_lookml(all_dashboards)
        dash_objs = self.create_Dashboard_obj(all_dashboards)
        return dash_objs
    
ini = "/usr/local/google/home/belvederej/Code/ini_files/joe.ini"
sdk = looker_sdk.init40(config_file=ini)
test = CaptureDashboards(sdk)
test.execute()