from lmanage.utils.errorhandling import return_sleep_message, calc_done_percent
from lmanage.utils.looker_object_constructors import DashboardObject
from progress.bar import ChargingBar
import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


class CaptureDashboards():

    def __init__(self, sdk):
        self.sdk = sdk

    def get_all_dashboards(self) -> dict:
        all_dashboards = self.sdk.all_dashboards()
        scrub_dashboards = {dash.id: dash.folder.id for dash in all_dashboards if not dash.folder.is_personal or dash.folder.is_embed}
        return scrub_dashboards

    def get_dashboard_lookml(self, all_dashboards: list) -> list:
        bar = ChargingBar('Dashboard Capture Progress', max=len(all_dashboards))
        response = []
        count = 0
        for dash_id in all_dashboards:
            count += 1
            lookml = None
            trys = 0
            while lookml is None:
                trys += 1
                try:
                    lookml = self.sdk.dashboard_lookml(dashboard_id=dash_id)
                except:
                    return_sleep_message(call_number=trys)

            captured_dashboard = DashboardObject(
                legacy_folder_id=all_dashboards.get(dash_id),
                lookml=lookml.lookml,
                dashboard_id=dash_id)
            response.append(captured_dashboard)
            
            percent_complete = calc_done_percent(iterator=count, total=len(all_dashboards))
            bar.next()
        bar.finish

        return response

    def execute(self):
        all_dashboards = self.get_all_dashboards()
        captured_dash = self.get_dashboard_lookml(all_dashboards)
        return captured_dash
