from tqdm import tqdm
from looker_sdk import models40 as models
from lmanage.utils import logger_creation as log_color
# logger = log_color.init_logger(__name__, logger_level)
from lmanage.configurator.create_object import CreateObject


class CreateSchedules(CreateObject):
    def __init__(self, sdk, folder_mapping, content_metadata) -> None:
        self.sdk = sdk
        self.folder_mapping = folder_mapping
        self.content_metadata = content_metadata

    def create_schedule(self) -> None:
        resp = []
        for dashboard in tqdm(self.content_metadata, desc="Schedule Creation", unit="schedule", colour="#2c8558"):
            if dashboard['scheduled_plans']:
                dashboard_id = self.sdk.search_dashboards(
                    slug=dashboard['dashboard_slug'], fields='id')[0].id
                for schedule in dashboard['scheduled_plans']:
                    destinations = []
                    for d in schedule['scheduled_plan_destination']:
                        destination = models.ScheduledPlanDestination()
                        destination.__dict__.update(d)
                        destinations.append(destination)
                    body = models.WriteScheduledPlan(
                        name=schedule['name'],
                        # user_id="1",
                        run_as_recipient=schedule['run_as_recipient'],
                        enabled=schedule['enabled'],
                        look_id=schedule['look_id'],
                        dashboard_id=dashboard_id,
                        # lookml_dashboard_id=schedule['lookml_dashboard_id'],
                        scheduled_plan_destination=destinations,
                        filters_string=schedule['filters_string'],
                        dashboard_filters=schedule['dashboard_filters'],
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
                    plan = self.sdk.create_scheduled_plan(body=body)
                    resp.append(plan)
        return resp

    def execute(self):
        mapping = self.create_schedule()
        return mapping

    # write get all dashboards from looker sdk
