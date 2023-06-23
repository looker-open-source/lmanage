import logging
from looker_sdk import models40 as models, error
from tqdm import tqdm
from tenacity import retry, wait_fixed, wait_random, stop_after_attempt

class CreateInstanceLooks():
    def __init__(self, folder_mapping, sdk, content_metadata, logger):
        self.sdk = sdk
        self.content_metadata = content_metadata
        self.folder_mapping = folder_mapping
        self.logger = logger

    def create_query(self, look_metadata: dict) -> int:
        '''create a query from look metadata and return the id'''
        query_body = models.WriteQuery(
            model=look_metadata['query_obj']['model'] if look_metadata['query_obj']['model'] else None,
            view=look_metadata['query_obj']['view'] if look_metadata['query_obj']['view'] else None,
            fields=look_metadata['query_obj']['fields'] if look_metadata['query_obj']['fields'] else None,
            pivots=look_metadata['query_obj']['pivots'] if look_metadata['query_obj']['pivots'] else None,
            fill_fields=look_metadata['query_obj']['fill_fields'] if look_metadata['query_obj']['fill_fields'] else None,
            filters=look_metadata['query_obj']['filters'] if look_metadata['query_obj']['filters'] else None,
            filter_expression=look_metadata['query_obj']['filter_expression'] if look_metadata['query_obj']['filter_expression'] else None,
            sorts=look_metadata['query_obj']['sorts'] if look_metadata['query_obj']['sorts'] else None,
            limit=look_metadata['query_obj']['limit'] if look_metadata['query_obj']['limit'] else None,
            column_limit=look_metadata['query_obj']['column_limit'] if look_metadata['query_obj']['column_limit'] else None,
            total=look_metadata['query_obj']['total'] if look_metadata['query_obj']['total'] else None,
            row_total=look_metadata['query_obj']['row_total'] if look_metadata['query_obj']['row_total'] else None,
            subtotals=look_metadata['query_obj']['subtotals'] if look_metadata['query_obj']['subtotals'] else None,
            vis_config=look_metadata['query_obj']['vis_config'] if look_metadata['query_obj']['vis_config'] else None,
            filter_config=look_metadata['query_obj']['filter_config'] if look_metadata['query_obj']['filter_config'] else None,
            visible_ui_sections=look_metadata['query_obj']['visible_ui_sections'] if look_metadata['query_obj']['visible_ui_sections'] else None,
            dynamic_fields=look_metadata['query_obj']['dynamic_fields'] if look_metadata['query_obj']['dynamic_fields'] else None,
            query_timezone=look_metadata['query_obj']['query_timezone'] if look_metadata['query_obj']['query_timezone'] else None
        )
        response = self.sdk.create_query(body=query_body)
        return response

    def create_look(self, query_id: int, look_metadata: dict, folder_mapping: dict) -> dict:
        legacy_fid = look_metadata.get('legacy_folder_id')
        look_body = models.WriteLookWithQuery(
            title=look_metadata.get('title'),
            description=look_metadata['description'],
            query_id=query_id,
            folder_id=folder_mapping.get(legacy_fid) if folder_mapping.get(legacy_fid) != 'Shared' else '1') 
        response = self.sdk.create_look(body=look_body)
        return response

    def execute(self) -> dict:
        look_mapping = []

        for look in tqdm(self.content_metadata, desc="Look Creation", unit=" attributes", colour="#2c8558"):
            query = self.create_query(look_metadata=look)
            new_look = self.create_look(
                query_id=query.id, look_metadata=look, folder_mapping=self.folder_mapping)
            temp = {}
            temp['look_mapping'] = {}
            temp['look_mapping'][look.get('look_id')] = new_look.get('id')
            temp['folder_mapping'] = {}
            temp['folder_mapping'][look.get('legacy_folder_id')] = self.folder_mapping.get(
                look.get('legacy_folder_id'))
            look_mapping.append(temp)

        return look_mapping
