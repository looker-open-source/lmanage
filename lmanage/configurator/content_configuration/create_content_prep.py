from tqdm import tqdm
from looker_sdk import models40 as models
import yaml 
import coloredlogs
import logging
from lmanage.utils.looker_object_constructors import DashboardObject
from lmanage.utils.errorhandling import return_sleep_message
logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')

class CleanInstanceContent():
    def __init__(self, sdk) -> None:
        self.sdk = sdk


    def empty_looker_dashboard_trash(self) -> None:
        trash_dash = self.sdk.search_dashboards(deleted='True')
        trash_dash_id_list = [dash.id for dash in trash_dash]
        for dash_id in tqdm(trash_dash_id_list, 'Scrubbing Dash', unit='dashboards',colour="#2c8558"):
            self.sdk.delete_dashboard(dashboard_id=dash_id)
            logger.debug(f'cleaning the trash dashboard {dash_id} from instance')

    def empty_looker_look_trash(self) -> None:
        trash_look = self.sdk.search_looks(deleted='true')
        trash_look_id_list = [look.id for look in trash_look]
        for look_id in tqdm(trash_look_id_list, 'Scrubbing Look', unit='Look', colour="#2c8558"):
            self.sdk.delete_look(look_id=look_id)
            logger.debug(
                f'cleaning the trash dashboard {look_id} from instance')


    def execute(self):
        self.empty_looker_dashboard_trash()
        self.empty_looker_look_trash()