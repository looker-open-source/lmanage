import looker_sdk
import calendar
import time
import json
from lmanage.utils.errorhandling import return_sleep_message

class CaptureDashboards():

    def __init__(self, sdk):
        self.sdk = sdk

    def get_all_dashboards(self):

        all_dashboards = None
        trys = 0
        while all_dashboards is None:
            trys += 1
            try:
                all_dashboards = self.sdk.all_dashboards()
            except:
                return_sleep_message(call_number=trys)

        return all_dashboards
    
    
    def get_dashboard_lookml(self, all_dashboards):
        
        for dash in all_dashboards:
            lookml = None
            trys = 0
            while lookml is None:
                trys += 1
                try:
                    lookml = self.sdk.dashboard_lookml(dashboard_id=dash.id)
                except: 
                    return_sleep_message(call_number=trys)
            
            dash.lookml = lookml.lookml
        
        return all_dashboards
    
    def convert_dashboards_to_json(self, all_dashboards):
        for index, dash in enumerate(all_dashboards): 
            all_dashboards[index] = dash.__dict__
            all_dashboards[index]['folder'] = dash['folder'].__dict__
            all_dashboards[index]['folder']['created_at'] = str(dash['folder']['created_at'])

        json_data = json.dumps(all_dashboards)
        return json_data 

    def create_dashboard_files(self, json_data):
        gmt = time.gmtime()
        ts = calendar.timegm(gmt)
        with open("./lmanage/capturator/dashboard_capturation/captured_dashboards/looker_dashboards_" + str(ts) + ".json", "w") as file:
            json.dump(json_data, file)

    def execute(self):
        all_dashboards = self.get_all_dashboards()
        all_dashboards = self.get_dashboard_lookml(all_dashboards)
        json_data = self.convert_dashboards_to_json(all_dashboards)
        self.create_dashboard_files(json_data)