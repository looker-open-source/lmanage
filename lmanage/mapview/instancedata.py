from looker_sdk import models
import json


def get_dashboards(sdk):
    """Uses the Looker SDK System__Activity model to extract dashboard
    and dashboard_element metadata.

    Simple run_inline_query call to Looker SDK
    Args:
        sdk: Looker SDK object
    Returns:
        An dict response with the dashboard and dashboard_element metadata.
        For example:
    [{'dashboard.id': 1,
         'dashboard_element.id': 1,
         'dashboard_element.type': 'vis',
         'dashboard_element.result_source': 'Lookless',
         'query.model': 'bq',
         'query.view': 'order_items',
         'query.formatted_fields': '["order_items.count"]',
         'query.id': 59,
         'dashboard.title': 'dash_1',
         'look.id': None}]
    """
    query_config = models.WriteQuery(
        model="system__activity",
        view="dashboard",
        fields=[
            "dashboard.id",
            "dashboard_element.id",
            "dashboard_element.type",
            "dashboard_element.result_source",
            "query.model",
            "query.view",
            "query.formatted_fields",
            "query.id",
            "dashboard.title",
            "look.id"
        ],
        filters={
            "dashboard_element.type": "-text",
            "dashboard.deleted_date": "NULL"
        },
        limit='5000'
    )
    query_response = sdk.run_inline_query(
        result_format='json',
        body=query_config
    )

    query_response = json.loads(query_response)

    return query_response
