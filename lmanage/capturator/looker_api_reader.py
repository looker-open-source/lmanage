from lmanage.capturator.folder_capturation import folder_config as fc
from lmanage.capturator.user_group_capturation import role_config as rc
from lmanage.capturator.user_attribute_capturation import capture_ua_permissions as cup
from lmanage.capturator.content_capturation import dashboard_capture as dc, look_capture as lc, board_capture as bc
from lmanage.looker_config import LookerConfig
from lmanage.logger_config import setup_logger
from lmanage.looker_auth import LookerAuth

logger = setup_logger()


class LookerApiReader():
    shared_folder_id = '1'

    def __init__(self, ini_file):
        self.sdk = LookerAuth().authenticate(ini_file)

    def get_config(self) -> LookerConfig:
        settings = self.__read_settings()
        content = self.__read_content()
        return LookerConfig(settings, content)

    def __read_settings(self):
        # Folder configuration
        folder_returns = fc.CaptureFolderConfig(
            sdk=self.sdk, logger=logger).execute()
        folder_structure_list = folder_returns[1]
        self.content_folders = [self.shared_folder_id] + folder_returns[0]

        # Roles, Permission Sets & Model Sets
        role_info = rc.ExtractRoleInfo(sdk=self.sdk, logger=logger)
        permission_sets = role_info.extract_permission_sets()
        model_sets = role_info.extract_model_sets()
        roles = role_info.extract_role_info()

        # User Attributes
        user_attributes = cup.ExtractUserAttributes(
            sdk=self.sdk, logger=logger).create_user_attributes()

        return {
            'folder_permissions': folder_structure_list,
            'permission_sets': permission_sets,
            'model_sets': model_sets,
            'roles': roles,
            'user_attributes': user_attributes
        }

    def __read_content(self):
        # Boards
        # boards = bc.CaptureBoards(sdk=sdk).execute()

        # Looks
        looks = lc.LookCapture(
            sdk=self.sdk, content_folders=self.content_folders, logger=logger).execute()

        # Dashboards
        dashboards = dc.CaptureDashboards(
            sdk=self.sdk, content_folders=self.content_folders, logger=logger, all_alerts=self.sdk.search_alerts()).execute()

        return {
            'looks': looks,
            'dashboards': dashboards
        }
