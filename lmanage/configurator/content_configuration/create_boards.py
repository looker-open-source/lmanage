from tqdm import tqdm
from looker_sdk import models40 as models
from lmanage.utils import logger_creation as log_color
#logger = log_color.init_logger(__name__, logger_level)

class Create_Boards():

    def __init__(self, sdk, board_metadata, dashboard_mapping, look_mapping) -> None:
        self.sdk = sdk
        self.dashboard_mapping = dashboard_mapping 
        self.look_mapping =look_mapping 
        self.board_metadata = board_metadata

    def create_boards(self, bmeta: dict):
        board_body = models.WriteBoard(
            description=bmeta.get('description'),
            title=bmeta.get('title'),
            section_order=bmeta.get('section_order')
        )

        board = self.sdk.create_board(body=board_body)

        return board

    def create_board_section(self,section_object, board_id):
        new_board_section = models.WriteBoardSection(
            board_id=board_id,
            description=section_object.description,
            item_order=section_object.item_order,
            title=section_object.title
        )
        resp = self.sdk.create_board_section(body=new_board_section)
        return resp.id

    def match_dashboard_id(self, source_dashboard_id: str) -> str:
        pass
    def match_look_id(self, source_look_id: str) -> str:
        pass


    def create_board_item(self, target_board_section_id):

        dashboard_id = None
        look_id = None

        if target_board_section_id.dashboard_id:
            dashboard_id = self.match_dashboard_id(target_board_section_id.dashboard_id)
        if target_board_section_id.look_id:
            look_id = self.match_look_id(target_board_section_id.look_id)

        new_board_item = models.WriteBoardItem()
        new_board_item.__dict__.update(source_board_item_object.__dict__)
        new_board_item.dashboard_id = dashboard_id
        new_board_item.look_id = look_id
        new_board_item.homepage_section_id = target_board_section_id

        logger.info(
            "Creating item",
            extra={
                "section_id": new_board_item.homepage_section_id,
                "dashboard_id": new_board_item.dashboard_id,
                "look_id": new_board_item.look_id,
                "url": new_board_item.url
            }
        )
        resp = target_sdk.create_homepage_item(new_board_item)
        logger.info("Item created", extra={"id": resp.id})

        return resp


    def execute(self):
        '''
        create boards
        in boards create sections
        in sections create board items
        check content access provisions
        '''
        for board in self.board_metadata:
            nb = self.create_boards(bmeta=board)
            
            print(nb)
