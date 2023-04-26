from tqdm import tqdm
import coloredlogs
import logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')

class CleanInstanceContent():
    def __init__(self, sdk) -> None:
        self.sdk = sdk

    def empty_looker_dashboard_trash(self) -> None:
        trash_dash = self.sdk.search_dashboards(deleted=True)
        trash_dash_id_list = [dash.id for dash in trash_dash]
        for dash_id in tqdm(trash_dash_id_list, 'Emptying Dashboard Trash', unit='dashboards', colour="#2c8558"):
            self.sdk.delete_dashboard(dashboard_id=dash_id)
            logger.debug(
                f'cleaning the trash dashboard {dash_id} from instance')

    def empty_looker_look_trash(self) -> None:
        trash_look = self.sdk.search_looks(deleted=True)
        trash_look_id_list = [look.id for look in trash_look]
        for look_id in tqdm(trash_look_id_list, 'Emptying Look Trash', unit='Look', colour="#2c8558"):
            self.sdk.delete_look(look_id=look_id)
            logger.debug(
                f'cleaning the trash dashboard {look_id} from instance')

    def delete_instance_dash(self, dashboards: list) -> None:
        delete_id_list = [dash.id for dash in dashboards]
        for dash_id in tqdm(delete_id_list, 'Scrubbing Instance Dashboards', unit='dashboards', colour="#2c8558"):
            self.sdk.delete_dashboard(dashboard_id=dash_id)
            logger.debug(
                f'cleaning the trash dashboard {dash_id} from instance')

    def delete_instance_look(self, looks: list) -> None:
        delete_id_list = [look.id for look in looks]
        for look_id in tqdm(delete_id_list, 'Scrubbing Instance Looks', unit='looks', colour="#2c8558"):
            self.sdk.delete_look(look_id=look_id)
            logger.debug(
                f'cleaning the trash dashboard {look_id} from instance')

    def execute(self):
        all_dash_list = self.sdk.all_dashboards()
        all_look_list = self.sdk.all_looks()
        self.delete_instance_dash(dashboards=all_dash_list)
        self.delete_instance_look(looks=all_look_list   )
        self.empty_looker_dashboard_trash()
        self.empty_looker_look_trash()
