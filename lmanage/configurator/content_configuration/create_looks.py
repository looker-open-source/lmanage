import logging
from looker_sdk import models40 as models, error
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')
logging.getLogger("requests").setLevel(logging.WARNING)


class CreateInstanceLooks():
    def __init__(self, folder_mapping, sdk, content_metadata):
        self.sdk = sdk
        self.content_metadata = content_metadata
        self.folder_mapping = folder_mapping

    def create_query(self, look_metadata: dict) -> int:
        '''create a query from look metadata and return the id'''
        query_body = models.WriteQuery(
            model=look_metadata['query_obj']['model'],
            view=look_metadata['query_obj']['view'],
            fields=look_metadata['query_obj']['fields'],
            pivots=look_metadata['query_obj']['pivots'],
            fill_fields=look_metadata['query_obj']['fill_fields'],
            filters=look_metadata['query_obj']['filters'],
            filter_expression=look_metadata['query_obj']['filter_expression'],
            sorts=look_metadata['query_obj']['sorts'],
            limit=look_metadata['query_obj']['limit'],
            column_limit=look_metadata['query_obj']['column_limit'],
            total=look_metadata['query_obj']['total'],
            row_total=look_metadata['query_obj']['row_total'],
            subtotals=look_metadata['query_obj']['subtotals'],
            vis_config=look_metadata['query_obj']['vis_config'],
            filter_config=look_metadata['query_obj']['filter_config'],
            visible_ui_sections=look_metadata['query_obj']['visible_ui_sections'],
            dynamic_fields=look_metadata['query_obj']['dynamic_fields'],
            query_timezone=look_metadata['query_obj']['query_timezone']
        )
        response = self.sdk.create_query(body=query_body)
        return response

    def create_look(self, query_id: int, look_metadata: dict, folder_mapping: dict) -> dict:
        legacy_fid=look_metadata.get('legacy_folder_id')
        look_body = models.WriteLookWithQuery(
                title=look_metadata.get('title'),
                description=look_metadata['description'],
                query_id=query_id,
                folder_id=folder_mapping.get(legacy_fid))
        response = self.sdk.create_look(body=look_body)
        return response
        
    def execute(self) -> dict:
        look_mapping = []


        for look in self.content_metadata:
            query = self.create_query(look_metadata=look)
            new_look = self.create_look(query_id=query.id, look_metadata=look, folder_mapping=self.folder_mapping)
            temp = {}
            temp['look_mapping'] = {}
            temp['look_mapping'][look.get('look_id')] =new_look.get('id')
            temp['folder_mapping'] = {}
            temp['folder_mapping'][look.get('legacy_folder_id')] = self.folder_mapping.get(look.get('legacy_folder_id'))
            look_mapping.append(temp)
            
        return look_mapping
