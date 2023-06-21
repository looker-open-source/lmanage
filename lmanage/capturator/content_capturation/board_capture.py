from tqdm import tqdm
import logging
from lmanage.utils.errorhandling import return_sleep_message
from lmanage.utils.looker_object_constructors import BoardObject
from lmanage.utils import logger_creation as log_color
from yaspin import yaspin
#logger = log_color.init_logger(__name__, logger_level)


class CaptureBoards():
    def __init__(self, sdk):
        self.sdk = sdk

    def handle_board_structure(self, board_response: dict) -> dict:
        board_section_list = board_response.board_sections
        bs_list = []

        for board_section in board_section_list:
            board_item_list = board_section.board_items
            new_bi_list = [board_item.__dict__ for board_item in board_item_list] 
            board_section['board_items'] = new_bi_list
            bs_dict = board_section.__dict__
            bs_list.append(bs_dict)

        board_response['board_sections'] = bs_list

        return board_response 
               

    def get_all_boards(self) -> dict:
        response = []
        with yaspin().white.bold.shark.on_blue as sp:
            sp.text="getting all system board metadata (can take a while)"
            all_system_boards = self.sdk.all_boards()
        
        for board in all_system_boards:
            bresponse = self.handle_board_structure(board_response=board)
            b = BoardObject(
                content_metadata_id=board.content_metadata_id,
                section_order=board.section_order,
                title=board.title,
                primary_homepage=board.primary_homepage,
                description=board.description,
                board_sections=bresponse.board_sections
            )
            response.append(b)
        return response


    def execute(self):
        all_boards = self.get_all_boards()
        return all_boards