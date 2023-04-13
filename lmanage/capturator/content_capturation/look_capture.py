import logging
import time
import coloredlogs
import lmanage.utils.looker_object_constructors as loc
from lmanage.utils.errorhandling import return_sleep_message, calc_done_percent
from progress.bar import ChargingBar
from progress.spinner import Spinner

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


class CaptureLookObject():
    def __init__(self, sdk):
        self.sdk = sdk

    def all_looks(self):
        spinner = Spinner('loading')
        all_look_meta = None
        trys = 0
        while all_look_meta is None:
            try:
                with Spinner('Capturing all Look Metadata') as bar:
                    bar.next()
                    logger.debug('running the all look sdk call to get existing look metadata')
                    all_look_meta = self.sdk.all_looks()
            except:
                return_sleep_message
        all_looks_id = [look.id for look in all_look_meta]
        return all_looks_id

    def get_look_metadata(self, look_id: str) -> dict:
        look_meta = None
        trys = 0
        while look_meta is None:
            try:
                look_meta = self.sdk.look(look_id=look_id)
            except:
                return_sleep_message
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
        bar = ChargingBar('Look Capture Progress', max=len(all_look_data))
        looks = []
        content = 1
        for look in all_look_data:
            total = len(all_look_data)
            lmetadata = self.get_look_metadata(look_id=look)
            if lmetadata.folder.is_personal:
                pass
            elif lmetadata.folder.is_embed:
                pass
            else:
                query_object = lmetadata.query.__dict__
                nq_obj = self.clean_query_obj(query_metadata=query_object)

                legacy_folder = lmetadata.folder_id
                look_id = lmetadata.id
                title = lmetadata.title
                look_obj = loc.LookObject(
                    query_obj=nq_obj,
                    description=lmetadata.description,
                    legacy_folder_id=legacy_folder,
                    look_id=look_id,
                    title=title)
                looks.append(look_obj)
            content += 1
            bar.next()
        bar.finish()
        return looks
