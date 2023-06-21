from tqdm import tqdm
from looker_sdk import models40 as models
from lmanage.utils import logger_creation as log_color
#logger = log_color.init_logger(__name__, logger_level)

class Create_Schedules():

    def __init__(self, sdk, folder_mapping, content_metadata) -> None:
        self.sdk = sdk
        self.folder_mapping = folder_mapping
        self.content_metadata = content_metadata

    
    def create_schedule(self) -> None:
        resp = []
        for dash in tqdm(self.content_metadata, desc = "Schedule Creation", unit="schedule", colour="#2c8558"):
            if dash['schedule_plans']:
                for schedule in dash['schedule_plans']:
                    new_dash_id = self.sdk.search_dashboards(slug=dash['dashboard_slug'], fields='id')[0].id
                    body = models.WriteScheduledPlan(
                        user_id=2
                    )
                    x = models.ScheduledPlanDestination()
                    test = []
                    for destination in schedule['scheduled_plan_destination']:
                        x.__dict__.update(destination)
                        test.append(x)
                    appendthing = {'scheduled_plan_destination': test}
                    body.__dict__.update(schedule)
                    body.__dict__.update(appendthing)
                    body.__dict__.pop('user')
                    body.user_id = 2
                    body.dashboard_id = new_dash_id
                    plan = self.sdk.create_scheduled_plan(body=body)
                    resp.append(plan)

        return resp


    def execute(self):
        mapping = self.create_schedule()
        return mapping

    #write get all dashboards from looker sdk