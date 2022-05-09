from looker_sdk import models
import json


class GetCleanInstanceData():
    def __init__(self, sdk):
        self.sdk = sdk

    def get_dashboards(self):
        """Uses the Looker SDK System__Activity model to extract dashboard
        and dashboard_element metadata.
        """
        query_config = models.WriteQuery(
            model="system__activity",
            view="dashboard",
            fields=[
                "dashboard.id",
                "dashboard_element.id",
                "dashboard_element.type",
                "dashboard_element.result_source",
                "query.formatted_pivots",
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
        query_response = self.sdk.run_inline_query(
            result_format='json',
            body=query_config
        )

        query_response = json.loads(query_response)

        return query_response

    def unpivot_query(self, query_id):
        query_metadata = self.sdk.query(query_id=query_id)

        query_body = models.WriteQuery(
            model=query_metadata.model,
            view=query_metadata.view,
            fields=query_metadata.fields,
            filters=query_metadata.filters
        )

        new_query = self.sdk.create_query(body=query_body)
        return new_query.id

    def execute(self):
        instance_data = self.get_dashboards()
        clean_data = []
        for db_element in instance_data:
            if db_element['query.formatted_pivots'] is None:
                clean_data.append(db_element)
            else:
                query_id = db_element['query.id']
                nqid = self.unpivot_query(query_id)
                db_element['query.id'] = nqid
                clean_data.append(db_element)
        return clean_data
