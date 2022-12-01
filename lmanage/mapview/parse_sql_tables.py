import logging
import coloredlogs
from lmanage.mapview.utils import parsing_sql
from looker_sdk import error


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')
logging.getLogger("looker_sdk").setLevel(logging.WARNING)


class ParseSqlTables():
    def __init__(self, dataextract, sdk):
        self.dataextract = dataextract
        self.sdk = sdk

    def parse_sql(self, qid: int):
        """
        Idenfies the base tables and joins used by a Looker query.

        Iterates over a list of PyLookML files identifies view files aand returns a
        list of the sql_table_names if they exist in an object of type 'View'
            qid: (int) query_id from lmanage.a  Looker query
        Returns:
            A list of all the tables that are found from lmanage.a Looker generated
            SQL query.
            For example:
            ['public.order_items','public.inventory_items','public.events']
        Exception:
            If a query is broken for whatever reason the Exception is caught to
            continue the program running
        """
        try:
            sql_response = self.sdk.run_query(
                query_id=qid, result_format="sql")
            if isinstance(sql_response, str):
                tables = parsing_sql.extract_tables(sql_response)
                return tables
            else:
                return sql_response
        except error.SDKError:
            return('No Content')

    def get_sql_from_elements(self):
        """Amends returned SDK System__Activity reponse with sql tables used
        from lmanage.the `parse_sql` function.

        Iterates over the response from lmanage.get_dashboards and runs the parse_sql
        function for each returned dashboard element, returns the list of tables
        and amends the dict response and returns it
        Args:
            sdk: Looker SDK object
            content_results: (dict) response from lmanage.get_dashboards function call
        Returns:
            An amended dict response with the sql columns used by each element
            extracted our of the Looker generated SQL for each dashboard object.
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
             'look.id': None,
             'sql_joins': ['`looker-private-demo.ecomm.order_items`']}]
        """
        for dash in self.dataextract:
            query_id = dash['query.id']
            sql_value = self.parse_sql(query_id)

            dash['sql_joins'] = sql_value

        return self.dataextract
