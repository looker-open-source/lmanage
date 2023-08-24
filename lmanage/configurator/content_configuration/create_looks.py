import logging
from looker_sdk import models40 as models, error
from tqdm import tqdm
from tenacity import retry, wait_fixed, wait_random, stop_after_attempt
from lmanage.configurator.create_object import CreateObject
from lmanage.utils.helpers import nstr


class CreateLooks(CreateObject):
    def __init__(self, sdk, folder_mapping, content_metadata, logger):
        self.sdk = sdk
        self.folder_mapping = folder_mapping
        self.content_metadata = content_metadata
        self.logger = logger

    def execute(self) -> dict:
        look_mapping = []
        for look in tqdm(self.content_metadata, desc="Look Creation", unit="attributes", colour="#2c8558"):
            query = self.__create_query(look_metadata=look)
            created_look = self.__create_look(query.id, look)
            if 'scheduled_plans' in look and len(look['scheduled_plans']) > 0:
                self.__create_scheduled_plans(
                    look['scheduled_plans'], created_look.id)
            temp = {}
            temp['look_mapping'] = {}
            temp['look_mapping'][look.get('look_id')] = created_look.id
            temp['folder_mapping'] = {}
            temp['folder_mapping'][look.get('legacy_folder_id')] = self.folder_mapping.get(
                look.get('legacy_folder_id'))
            look_mapping.append(temp)
        return look_mapping

    def __create_query(self, look_metadata: dict) -> int:
        '''create a query from look metadata and return the id'''
        query_body = models.WriteQuery(
            model=look_metadata['query_obj']['model'] if look_metadata['query_obj']['model'] else None,
            view=look_metadata['query_obj']['view'] if look_metadata['query_obj']['view'] else None,
            fields=look_metadata['query_obj']['fields'] if look_metadata['query_obj']['fields'] else None,
            pivots=look_metadata['query_obj']['pivots'] if look_metadata['query_obj']['pivots'] else None,
            fill_fields=look_metadata['query_obj']['fill_fields'] if look_metadata['query_obj']['fill_fields'] else None,
            filters=look_metadata['query_obj']['filters'] if look_metadata['query_obj']['filters'] else None,
            filter_expression=look_metadata['query_obj']['filter_expression'] if look_metadata[
                'query_obj']['filter_expression'] else None,
            sorts=look_metadata['query_obj']['sorts'] if look_metadata['query_obj']['sorts'] else None,
            limit=look_metadata['query_obj']['limit'] if look_metadata['query_obj']['limit'] else None,
            column_limit=look_metadata['query_obj']['column_limit'] if look_metadata['query_obj']['column_limit'] else None,
            total=look_metadata['query_obj']['total'] if look_metadata['query_obj']['total'] else None,
            row_total=look_metadata['query_obj']['row_total'] if look_metadata['query_obj']['row_total'] else None,
            subtotals=look_metadata['query_obj']['subtotals'] if look_metadata['query_obj']['subtotals'] else None,
            vis_config=look_metadata['query_obj']['vis_config'] if look_metadata['query_obj']['vis_config'] else None,
            filter_config=look_metadata['query_obj']['filter_config'] if look_metadata['query_obj']['filter_config'] else None,
            visible_ui_sections=look_metadata['query_obj']['visible_ui_sections'] if look_metadata[
                'query_obj']['visible_ui_sections'] else None,
            dynamic_fields=look_metadata['query_obj']['dynamic_fields'] if look_metadata['query_obj']['dynamic_fields'] else None,
            query_timezone=look_metadata['query_obj']['query_timezone'] if look_metadata['query_obj']['query_timezone'] else None
        )
        response = self.sdk.create_query(body=query_body)
        return response

    def __create_look(self, query_id: int, look: dict) -> dict:
        old_folder_id = look.get('legacy_folder_id')
        new_folder_id = self.folder_mapping.get(old_folder_id)
        look_body = models.WriteLookWithQuery(
            title=look.get('title'),
            description=look['description'],
            query_id=query_id,
            folder_id=new_folder_id)
        return self.sdk.create_look(body=look_body)

    def __create_scheduled_plans(self, scheduled_plans, look_id):
        for schedule in scheduled_plans:
            destinations = []
            for d in schedule['scheduled_plan_destination']:
                destination = models.ScheduledPlanDestination()
                destination.__dict__.update(d)
                destinations.append(destination)
            body = models.WriteScheduledPlan(
                name=schedule['name'],
                run_as_recipient=schedule['run_as_recipient'],
                enabled=schedule['enabled'],
                look_id=look_id,
                scheduled_plan_destination=destinations,
                filters_string=nstr(schedule['filters_string']),
                require_results=schedule['require_results'],
                require_no_results=schedule['require_no_results'],
                require_change=schedule['require_change'],
                send_all_results=schedule['send_all_results'],
                crontab=schedule['crontab'],
                timezone=schedule['timezone'],
                datagroup=schedule['datagroup'],
                query_id=schedule['query_id'],
                include_links=schedule['include_links'],
                pdf_paper_size=schedule['pdf_paper_size'],
                pdf_landscape=schedule['pdf_landscape'],
                embed=schedule['embed'],
                color_theme=schedule['color_theme'],
                long_tables=schedule['long_tables'],
                inline_table_width=schedule['inline_table_width'],
            )
            self.sdk.create_scheduled_plan(body=body)
