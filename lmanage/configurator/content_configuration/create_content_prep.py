from tqdm import tqdm


class CleanInstanceContent():
    def __init__(self, sdk,logger) -> None:
        self.sdk = sdk
        self.logger = logger

    def empty_looker_dashboard_trash(self) -> None:
        trash_dash = self.sdk.search_dashboards(deleted=True)
        trash_dash_id_list = [dash.id for dash in trash_dash]
        for dash_id in tqdm(trash_dash_id_list, 'Emptying Dashboard Trash', unit='dashboards', colour="#2c8558"):
            self.sdk.delete_dashboard(dashboard_id=dash_id)
            self.logger.debug(
                f'cleaning the trash dashboard {dash_id} from instance')

    def empty_looker_look_trash(self) -> None:
        trash_look = self.sdk.search_looks(deleted=True)
        trash_look_id_list = [look.id for look in trash_look]
        for look_id in tqdm(trash_look_id_list, 'Emptying Look Trash', unit='Look', colour="#2c8558"):
            self.sdk.delete_look(look_id=look_id)
            self.logger.debug(
                f'cleaning the trash dashboard {look_id} from instance')

    def delete_boards(self, all_board: list) -> None:
        delete_board_list = [board.id for board in all_board]
        for board_id in tqdm(delete_board_list, 'Scrubbing Instance Boards', unit='boards', colour="#2c8558"):
            self.sdk.delete_board(board_id=board_id)
            self.logger.debug(
                f'cleaning the trash board {board_id} from instance')

    def delete_schedule_plans(self, schedule_list: list) -> None:
        schedule_plan_id_list = [schedule.id for schedule in schedule_list]
        for schedule_plan_id in tqdm(schedule_plan_id_list, 'Scrubbing Instance Schedules', unit='schedules', colour="#2c8558"):
            self.sdk.delete_scheduled_plan(scheduled_plan_id=schedule_plan_id)
            self.logger.debug(f'cleaning the trash schedule {schedule_plan_id}')

    def delete_instance_dash(self, dashboards: list) -> None:
        delete_id_list = [
            dash.id for dash in dashboards if '::' not in dash.id]
        for dash_id in tqdm(delete_id_list, 'Scrubbing Instance Dashboards', unit='dashboards', colour="#2c8558"):
            self.sdk.delete_dashboard(dashboard_id=dash_id)
            self.logger.debug(
                f'cleaning the trash dashboard {dash_id} from instance')

    def delete_instance_look(self, looks: list) -> None:
        delete_id_list = [look.id for look in looks]
        for look_id in tqdm(delete_id_list, 'Scrubbing Instance Looks', unit='looks', colour="#2c8558"):
            self.sdk.delete_look(look_id=look_id)
            self.logger.debug(
                f'cleaning the trash dashboard {look_id} from instance')

    def execute(self):
        all_dash_list = self.sdk.all_dashboards()
        all_look_list = self.sdk.all_looks()
        all_board_list = self.sdk.all_boards()
        all_schedules_list = self.sdk.all_scheduled_plans(all_users=True)
        self.delete_instance_dash(dashboards=all_dash_list)
        self.delete_instance_look(looks=all_look_list)
        self.delete_boards(all_board=all_board_list)
        self.delete_schedule_plans(schedule_list=all_schedules_list)
        self.empty_looker_dashboard_trash()
        self.empty_looker_look_trash()
