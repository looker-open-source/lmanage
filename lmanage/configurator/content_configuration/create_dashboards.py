import json
from tqdm import tqdm
from looker_sdk import models40 as models, error
from lmanage.utils import logger_creation as log_color
from lmanage.configurator.create_object import CreateObject
from tenacity import (
    retry,
    wait_fixed,
    wait_random,
    stop_after_attempt,
    retry_if_exception_type,
)

# logger = log_color.init_logger(__name__, logger_level)


class NonRetryableError(Exception):
    """Custom exception for non-retryable errors."""

    pass


class CreateDashboards(CreateObject):
    def __init__(self, sdk, folder_mapping, content_metadata, logger) -> None:
        self.sdk = sdk
        self.alert_owner_id = sdk.me().id
        self.folder_mapping = folder_mapping
        self.content_metadata = content_metadata
        self.logger = logger

    def execute(self):
        mapping = self.__create_dashboards()
        self.logger.debug(mapping)
        return mapping

    @retry(
        wait=wait_fixed(3) + wait_random(0, 2),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(error.SDKError),
    )
    def __create_dashboard(
        self, dashboard_id, old_folder_id, folder_id, lookml
    ) -> None:
        try:
            created_dashboard = self.sdk.import_dashboard_from_lookml(
                body=models.WriteDashboardLookml(folder_id=folder_id, lookml=lookml)
            )
            return created_dashboard
        except error.SDKError as e:
            if (
                e.errors
                and hasattr(e.errors[0], "message")
                and e.errors[0].message == "Filter with this title already exists."
            ):
                self.logger.error(
                    f"Dashboard {dashboard_id} in folder {old_folder_id} failed with 'Filter with this title already exists' error."
                )
                raise NonRetryableError(
                    "Non-retryable error encountered, skipping retries."
                )
            else:
                self.logger.error(
                    f"Dashboard {dashboard_id} in folder {old_folder_id} failed with '{e.message}' error."
                )
                raise

    def __create_dashboards(self) -> None:
        for dashboard in tqdm(
            self.content_metadata,
            desc="Dashboard Upload",
            unit="dashboards",
            colour="#2c8558",
        ):
            self.logger.debug(type(dashboard))
            old_folder_id = dashboard.get("legacy_folder_id").get("folder_id")
            new_folder_id = self.folder_mapping.get(old_folder_id)

            try:
                created_dashboard = self.__create_dashboard(
                    dashboard.get("dashboard_id"),
                    old_folder_id,
                    new_folder_id,
                    dashboard.get("lookml"),
                )
            except NonRetryableError:
                continue

            if "scheduled_plans" in dashboard and len(dashboard["scheduled_plans"]) > 0:
                self.__create_scheduled_plans(
                    dashboard["scheduled_plans"], created_dashboard.id
                )

            if "alerts" in dashboard and len(dashboard["alerts"]) > 0:
                self.__create_alerts(
                    dashboard.get("dashboard_id"),
                    dashboard["alerts"],
                    dashboard["dashboard_element_alert_counts"],
                    created_dashboard.dashboard_elements,
                )

    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def __create_alerts(self, dashboard_id, alerts, alert_counts, dashboard_elements):
        alert_index = 0
        alert_count_index = 0
        for element in dashboard_elements:
            alert_count = int(alert_counts[alert_count_index])
            for _ in range(alert_count):
                alert = alerts[alert_index]
                applied_dashboard_filters = [
                    f
                    for f in alert["applied_dashboard_filters"]
                    if f["filter_title"] != ""
                ]
                field = alert["field"]
                element_id = element.id
                alert_body = json.dumps(
                    {
                        "cron": alert["cron"],
                        "custom_title": alert["custom_title"],
                        "dashboard_element_id": element_id,
                        "applied_dashboard_filters": applied_dashboard_filters,
                        "comparison_type": alert["comparison_type"],
                        "destinations": alert["destinations"],
                        "field": {
                            "title": field["title"],
                            "name": field["name"],
                            "filter": field["filter"],
                        },
                        "is_disabled": alert["is_disabled"],
                        "is_public": alert["is_public"],
                        "threshold": alert["threshold"],
                        "owner_id": self.alert_owner_id,
                    }
                )
                try:
                    self.sdk.create_alert(body=alert_body)
                except error.SDKError as e:
                    self.logger.warning(
                        f"Error creating alert with cron {alert['cron']} on dashboard with id {dashboard_id}: {e.message}"
                    )
                    self.logger.warning(e.errors)
                alert_index += 1
            alert_count_index += 1

    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def __create_scheduled_plans(self, scheduled_plans, dashboard_id):
        for schedule in scheduled_plans:
            destinations = []
            for d in schedule["scheduled_plan_destination"]:
                # destination = models.ScheduledPlanDestination()
                # destination.__dict__.update(d)
                destinations.append(d)
            body = models.WriteScheduledPlan(
                name=schedule["name"],
                run_as_recipient=schedule["run_as_recipient"],
                enabled=schedule["enabled"],
                dashboard_id=dashboard_id,
                scheduled_plan_destination=destinations,
                filters_string=schedule["filters_string"],
                require_results=schedule["require_results"],
                require_no_results=schedule["require_no_results"],
                require_change=schedule["require_change"],
                send_all_results=schedule["send_all_results"],
                crontab=schedule["crontab"],
                timezone=schedule["timezone"],
                datagroup=schedule["datagroup"],
                query_id=schedule["query_id"],
                include_links=schedule["include_links"],
                pdf_paper_size=schedule["pdf_paper_size"],
                pdf_landscape=schedule["pdf_landscape"],
                embed=schedule["embed"],
                color_theme=schedule["color_theme"],
                long_tables=schedule["long_tables"],
                inline_table_width=schedule["inline_table_width"],
            )
            self.sdk.create_scheduled_plan(body=body)
