from tqdm import tqdm
from lmanage.configurator.create_object import CreateObject


class CleanInstanceContent(CreateObject):
    def __init__(self, sdk, logger) -> None:
        self.sdk = sdk
        self.logger = logger

    def execute(self):
        # self.__delete_boards()
        self.__delete_dashboards()
        self.__delete_looks()
        self.__delete_scheduled_plans()
        self.__empty_dashboard_trash()
        self.__empty_look_trash()

    def __delete_boards(self) -> None:
        all_boards = self.sdk.all_boards()
        delete_board_list = [board.id for board in all_boards]
        for board_id in tqdm(delete_board_list, 'Scrubbing Instance Boards', unit='boards', colour="#2c8558"):
            self.sdk.delete_board(board_id=board_id)
            self.logger.debug(
                f'cleaning the trash board {board_id} from instance')

    def __delete_dashboards(self) -> None:
        all_dashboards = self.sdk.all_dashboards()
        delete_id_list = [
            dash.id for dash in all_dashboards if '::' not in dash.id]
        for dash_id in tqdm(delete_id_list, 'Scrubbing Instance Dashboards', unit='dashboards', colour="#2c8558"):
            self.sdk.delete_dashboard(dashboard_id=dash_id)
            self.logger.debug(
                f'cleaning the trash dashboard {dash_id} from instance')

    def __delete_looks(self) -> None:
        all_looks = self.sdk.all_looks()
        delete_id_list = [look.id for look in all_looks]
        for look_id in tqdm(delete_id_list, 'Scrubbing Instance Looks', unit='looks', colour="#2c8558"):
            self.logger.debug(
                f'Deleting look {look_id} from instance')
            self.sdk.delete_look(look_id=look_id)

    def __delete_scheduled_plans(self) -> None:
        all_schedules = self.sdk.all_scheduled_plans(all_users=True)
        schedule_plan_id_list = [schedule.id for schedule in all_schedules]
        for schedule_plan_id in tqdm(schedule_plan_id_list, 'Scrubbing Instance Schedules', unit='schedules', colour="#2c8558"):
            self.sdk.delete_scheduled_plan(scheduled_plan_id=schedule_plan_id)
            self.logger.debug(
                f'cleaning the trash schedule {schedule_plan_id}')

    def __empty_dashboard_trash(self) -> None:
        trash_dash = self.sdk.search_dashboards(deleted=True)
        trash_dash_id_list = [dash.id for dash in trash_dash]
        for dash_id in tqdm(trash_dash_id_list, 'Emptying Dashboard Trash', unit='dashboards', colour="#2c8558"):
            self.sdk.delete_dashboard(dashboard_id=dash_id)
            self.logger.debug(
                f'cleaning the trash dashboard {dash_id} from instance')

    def __empty_look_trash(self) -> None:
        trash_look = self.sdk.search_looks(deleted=True)
        trash_look_id_list = [look.id for look in trash_look]
        for look_id in tqdm(trash_look_id_list, 'Emptying Look Trash', unit='Look', colour="#2c8558"):
            self.sdk.delete_look(look_id=look_id)
            self.logger.debug(
                f'cleaning the trash dashboard {look_id} from instance')
