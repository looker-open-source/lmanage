import json
import looker_sdk
from looker_sdk import models
from pathlib import Path
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
fh = logging.FileHandler('schedule_juggle.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

logger = logging.getLogger(__name__)


def get_schedule_hotspots(sdk: looker_sdk) -> json:
    query_config = models.WriteQuery(
        model="system__activity",
        view="scheduled_plan",
        fields=[
            "scheduled_plan.next_run_time",
            "scheduled_plan.count"
        ],
        filters={
            "scheduled_job.run_once": "No",
            "scheduled_plan.next_run_time": "NOT NULL"
        },
        limit='5000'
    )
    query_response = sdk.run_inline_query(
        result_format='json',
        body=query_config
    )

    query_response = json.loads(query_response)

    return query_response


def main(**kwargs):
    ini_file = kwargs.get("ini_file")

    sdk = looker_sdk.init31(config_file=ini_file)

    logger.info((get_schedule_hotspots(sdk)))


if __name__ == "__main__":
    main(
        ini_file='../../../ini/profserv.ini'
    )
