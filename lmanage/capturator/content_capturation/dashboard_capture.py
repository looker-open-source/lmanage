import looker_sdk
import calendar
import time
import yaml
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
    
    def create_Dashboard_obj(self, all_dashboards):
        dash_objs = []
        for dash in all_dashboards:
            dash_objs.append(DashboardObject(dash.folder.id,dash.lookml,dash.id))
        return dash_objs

    def execute(self):
        all_dashboards = self.get_all_dashboards()
        del all_dashboards[5:]

        all_dashboards = self.get_dashboard_lookml(all_dashboards)
        dash_objs = self.create_Dashboard_obj(all_dashboards)
        return dash_objs