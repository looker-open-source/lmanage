from lmanage.utils import looker_object_constructors as loc, errorhandling as eh, logger_creation as log_color
from tqdm import tqdm
from yaspin import yaspin
from tenacity import retry, wait_fixed, wait_random, stop_after_attempt

#logger = log_color.init_logger(__name__, logger_level)

class LookCapture:
    def __init__(self, sdk, folder_root, logger):
        self.sdk = sdk
        self.folder_root = folder_root
        self.logger = logger

    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def get_all_looks_metadata(self) -> list:
       response = self.sdk.all_looks(fields='id,folder') 
       return response

    def all_looks(self):
        system_folders = ['Users','Embed Users','Embed Groups']
        all_look_meta = None
        with yaspin().white.bold.shark.on_blue as sp:
            sp.text="getting all system look metadata (can take a while)"
            all_look_meta = self.get_all_looks_metadata()
            
        scrub_looks = {}
        for look in all_look_meta:
            if look.folder.id in self.folder_root or look.folder.id == '1':
                scrub_looks[look.id] = look.folder.id 
            else:
                continue

        return scrub_looks

    def get_look_metadata(self, look_id: str) -> dict:
        look_meta = None
        trys = 0
        while look_meta is None:
            try:
                look_meta = self.sdk.look(look_id=look_id)
            except:
                eh.return_sleep_message
        return look_meta

    def clean_query_obj(self, query_metadata: dict) -> dict:
        metadata_keep_keys = [
            "model",
            "view",
            "fields",
            "pivots",
            "fill_fields",
            "filters",
            "filter_expression",
            "sorts",
            "limit",
            "column_limit",
            "total",
            "row_total",
            "subtotals",
            "vis_config",
            "filter_config",
            "visible_ui_sections",
            "dynamic_fields",
            "query_timezone"]
        restricted_look_metadata = dict(
            (k, query_metadata[k]) for k in metadata_keep_keys)
        return restricted_look_metadata


    def execute(self):
        '''
        1. get all the looks and extract the id's
        2. iterate through the looks and extract metadata, only keep necessary fields to make a query for look transference
        3. create custom look object and add to list
        '''
        all_look_data = self.all_looks()
        looks = []
        content = 1
        for look in tqdm(all_look_data, desc = "Look Capture", unit=" looks", colour="#2c8558"):
            lmetadata = self.get_look_metadata(look_id=look)
            schedule_metadata= self.sdk.scheduled_plans_for_look(look_id=lmetadata.id, all_users=True)
            query_object = lmetadata.query.__dict__
            nq_obj = self.clean_query_obj(query_metadata=query_object)
            self.logger.debug(nq_obj)

            legacy_folder = lmetadata.folder_id
            look_id = lmetadata.id
            title = lmetadata.title
            look_obj = loc.LookObject(
                query_obj=nq_obj,
                description=lmetadata.description,
                legacy_folder_id=legacy_folder,
                look_id=look_id,
                title=title,
                schedule_plans=schedule_metadata)
            looks.append(look_obj)
            content += 1
        return looks
