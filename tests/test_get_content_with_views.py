#!/usr/bin/python
#
# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ast
import lmanage
import lookml
from lmanage import get_content_with_views as ipe


class MockSDK():
    def run_inline_query():
        pass

    def run_query():
        pass


class MockQuery():
    def __init__(self, fields, query_id):
        self.fields = fields
        self.query_id = query_id


'''Inserting setup for project'''
project = lookml.Project(
    path="./tests/test_lookml_files/the_look"
)

data = [{'dashboard.id': 1,
         'dashboard_element.id': 1,
         'dashboard_element.type': 'vis',
         'dashboard_element.result_source': 'Lookless',
         'query.model': 'bq',
         'query.view': 'order_items',
         'query.formatted_fields': '["order_items.created_month", "order_items.count"]',
         'query.id': 59,
         'dashboard.title': 'dash_1',
         'look.id': None,
         'sql_joins': ['`looker-private-demo.ecomm.order_items`']}]

match_data = {'dashboard_id': 1,
              'element_id': 1,
              'sql_joins': ['`looker-private-demo.ecomm.order_items`'],
              'fields_used': '["order_items.created_month", "order_items.count"]',
              'sql_table_name': [
                  '`looker-private-demo.ecomm.distribution_centers`',
                  '`looker-private-demo.ecomm.products`',
                  '`looker-private-demo.ecomm.users`',
                  '`looker-private-demo.ecomm.order_items`',
                  '`looker-private-demo.ecomm.inventory_items`',
                  '`looker-private-demo.ecomm.events`'],
              'potential_join': [
                  'order_items',
                  'order_facts',
                  'inventory_items',
                  'users',
                  'user_order_facts',
                  'products',
                  'repeat_purchase_facts',
                  'distribution_centers',
                  'test_ndt']}

sql_table_names = {
    'views_aws/distribution_centers.view.lkml': ['`looker-private-demo.ecomm.distribution_centers`'],
    'views_aws/products.view.lkml': ['`looker-private-demo.ecomm.products`'],
    'views_aws/users.view.lkml': ['`looker-private-demo.ecomm.users`']
}


def test_parse_sql_pivots(mocker):
    sdk = MockSDK()
    mocker.patch.object(sdk, "run_query")
    sdk.run_query.return_value = """
        WITH order_user_sequence_facts AS (select oi.user_id,oi.id as order_id,row_number() over(partition by oi.user_id order by oi.created_at asc ) as order_sequence,
                oi.created_at,
                MIN(oi.created_at) OVER(PARTITION BY oi.user_id) as first_ordered_date,
                LAG(oi.created_at) OVER (PARTITION BY oi.user_id ORDER BY oi.created_at asc) as previous_order_date,
                LEAD(oi.created_at) OVER(partition by oi.user_id ORDER BY oi.created_at) as next_order_date,
                DATEDIFF(DAY,CAST(oi.created_at as date),CAST(LEAD(oi.created_at) over(partition by oi.user_id ORDER BY oi.created_at) AS date)) as repurchase_gap
              from order_items oi
         )
        SELECT * FROM (
        SELECT *, DENSE_RANK() OVER (ORDER BY z___min_rank) as z___pivot_row_rank, RANK() OVER (PARTITION BY z__pivot_col_rank ORDER BY z___min_rank) as z__pivot_col_ordering, CASE WHEN z___min_rank = z___rank THEN 1 ELSE 0 END AS z__is_h
        ighest_ranked_cell FROM (
        SELECT *, MIN(z___rank) OVER (PARTITION BY "order_user_sequence_facts.created_at_month") as z___min_rank FROM (
        SELECT *, RANK() OVER (ORDER BY "order_user_sequence_facts.created_at_month" DESC, z__pivot_col_rank) AS z___rank FROM (
        SELECT *, DENSE_RANK() OVER (ORDER BY "users.gender" NULLS LAST) AS z__pivot_col_rank FROM (
        SELECT
            users.gender  AS "users.gender",
                (TO_CHAR(DATE_TRUNC('month', CONVERT_TIMEZONE('UTC', 'America/New_York', order_user_sequence_facts.created_at )), 'YYYY-MM')) AS "order_user_sequence_facts.created_at_month",
            COUNT(DISTINCT order_user_sequence_facts.user_id ) AS "order_user_sequence_facts.count"
        FROM public.order_items  AS order_items
        INNER JOIN public.users  AS users ON order_items.user_id = users.id
        LEFT JOIN public.inventory_items  AS inventory_items ON inventory_items.id = order_items.inventory_item_id
        LEFT JOIN order_user_sequence_facts ON users.id = order_user_sequence_facts.user_id
        WHERE (order_user_sequence_facts.order_sequence = 1
            )
        GROUP BY
            (DATE_TRUNC('month', CONVERT_TIMEZONE(
                'UTC', 'America/New_York', order_user_sequence_facts.created_at ))),
            1) ww
        ) bb WHERE z__pivot_col_rank <= 16384
        ) aa
        ) xx
        ) zz
         WHERE (z__pivot_col_rank <= 50 OR z__is_highest_ranked_cell = 1) AND (z___pivot_row_rank <= 500 OR z__pivot_col_ordering = 1) ORDER BY z___pivot_row_rank
            """

    test = ipe.parse_sql(sdk=sdk, qid=(777))
    expected_result = ["public.order_items", "public.users",
                       "public.inventory_items", "order_user_sequence_facts", "order_items"]
    assert isinstance(test, list)
    assert len(test) == 5
    assert sorted(test) == sorted(expected_result)


def test_parse_sql_redshift_simple(mocker):
    sdk = MockSDK()
    mocker.patch.object(sdk, "run_query")
    sdk.run_query.return_value = """
        SELECT
            COUNT(DISTINCT order_items.order_id ) AS "order_items.count"
        FROM
            "public"."order_items" AS "order_items"
        LIMIT 500
        """

    test = ipe.parse_sql(sdk=sdk, qid=(777))
    expected_result = ["public.order_items"]
    assert isinstance(test, list)
    assert len(test) == 1
    assert sorted(test) == sorted(expected_result)


def test_parse_sql_redshift(mocker):
    sdk = MockSDK()
    mocker.patch.object(sdk, "run_query")
    sdk.run_query.return_value = """
    WITH cs_user_order_ndt AS (SELECT
            order_items.user_id  AS user_id,
            COUNT(DISTINCT CASE WHEN (products.category = 'Jeans') THEN order_items.order_id  ELSE NULL END) AS count_orders_with_jeans,
            COALESCE(SUM(CASE WHEN ((TRIM(TO_CHAR(order_items.created_at , 'Day'))) = 'Thursday') THEN order_items.sale_price  ELSE NULL END), 0) AS total_revenue_on_thursdays
    FROM public.order_items  AS order_items
    LEFT JOIN public.inventory_items  AS inventory_items ON order_items.inventory_item_id = inventory_items.id
    LEFT JOIN public.products  AS products ON inventory_items.product_id = products.id

    GROUP BY 1)
    SELECT
            cs_user_order_ndt.total_revenue_on_thursdays AS "cs_user_order_ndt.total_revenue_on_thursdays",
            distribution_centers.latitude  AS "distribution_centers.latitude",
            inventory_items.id  AS "inventory_items.id",
            order_items.order_id  AS "order_items.order_id",
            products.cost  AS "products.cost",
            users.latitude  AS "users.latitude"
    FROM public.order_items  AS order_items
    LEFT JOIN public.users  AS users ON order_items.user_id = users.id
    LEFT JOIN public.inventory_items  AS inventory_items ON order_items.inventory_item_id = inventory_items.id
    LEFT JOIN public.products  AS products ON inventory_items.product_id = products.id
    LEFT JOIN public.distribution_centers  AS distribution_centers ON products.distribution_center_id = distribution_centers.id
    INNER JOIN cs_user_order_ndt ON order_items.user_id = cs_user_order_ndt.user_id

    GROUP BY 1,2,3,4,5,6
    ORDER BY 1
    LIMIT 500
    """

    test = ipe.parse_sql(sdk=sdk, qid=(777))
    expected_result = ["public.order_items", "public.inventory_items",
                       "public.products", "public.users", "public.distribution_centers", "cs_user_order_ndt"]

    assert isinstance(test, list)
    assert len(test) == 6
    assert sorted(test) == sorted(expected_result)


def test_parse_sql_bq(mocker):
    sdk = MockSDK()
    mocker.patch.object(sdk, "run_query")
    sdk.run_query.return_value = """
        WITH order_items_parameter_test AS (SELECT
                users.first_name  AS first_name
        FROM `looker-private-demo.ecomm.order_items`
             AS order_items
        LEFT JOIN `looker-private-demo.ecomm.users`
             AS users ON order_items.user_id = users.id

        WHERE
                (users.first_name = 'ABBEY')
        GROUP BY 1)
        SELECT
                distribution_centers.latitude  AS distribution_centers_latitude,
                inventory_items.cost  AS inventory_items_cost,
                "Fix your broken Content Please"  AS order_items_broken_content,
                order_items_parameter_test.first_name AS order_items_parameter_test_first_name,
                products.category  AS products_category,
                users.country  AS users_country
        FROM `looker-private-demo.ecomm.order_items`
             AS order_items
        LEFT JOIN `looker-private-demo.ecomm.users`
             AS users ON order_items.user_id = users.id
        LEFT JOIN `looker-private-demo.ecomm.inventory_items`
             AS inventory_items ON order_items.inventory_item_id = inventory_items.id
        LEFT JOIN `looker-private-demo.ecomm.products`
             AS products ON inventory_items.product_id = products.id
        LEFT JOIN `looker-private-demo.ecomm.distribution_centers`
             AS distribution_centers ON (CAST(products.distribution_center_id AS int64)) = distribution_centers.id
        LEFT JOIN order_items_parameter_test ON order_items_parameter_test.first_name = users.first_name

        GROUP BY 1,2,3,4,5,6
        ORDER BY 1
        LIMIT 500
        """

    test = ipe.parse_sql(sdk=sdk, qid=(777))
    expected_result = ["`looker-private-demo.ecomm.order_items`", "`looker-private-demo.ecomm.inventory_items`", "`looker-private-demo.ecomm.products`",
                       "`looker-private-demo.ecomm.users`", "`looker-private-demo.ecomm.distribution_centers`", "order_items_parameter_test"]
    assert isinstance(test, list)
    assert len(test) == 6
    assert sorted(test) == sorted(expected_result)


def test_parse_sql_bq_1327(mocker):
    sdk = MockSDK()
    mocker.patch.object(sdk, "run_query")
    sdk.run_query.return_value = """
         SELECT
            REGEXP_EXTRACT(_TABLE_SUFFIX,r'\\d\\d\\d\\d')  AS gsod_year,
            case when gsod.prcp = 99.99 then null else gsod.prcp end AS gsod_rainfall,
            AVG(( case when gsod.prcp = 99.99 then null else gsod.prcp end ) ) AS gsod_average_rainfall
        FROM `bigquery-public-data.noaa_gsod.gsod*`  AS gsod
        GROUP BY 1,2
        ORDER BY
            3 DESC
        LIMIT 500
        """
    test = ipe.parse_sql(sdk=sdk, qid=(777))
    expected_result = ["`bigquery-public-data.noaa_gsod.gsod*`"]
    assert isinstance(test, list)
    assert len(test) == 1
    assert sorted(test) == sorted(expected_result)


def test_parse_sql_snowflake(mocker):
    sdk = MockSDK()
    mocker.patch.object(sdk, "run_query")
    sdk.run_query.return_value = """
        SELECT
                distribution_centers."LATITUDE"  AS "distribution_centers.latitude",
                inventory_items."COST"  AS "inventory_items.cost",
                order_items."INVENTORY_ITEM_ID"  AS "order_items.inventory_item_id",
                products."BRAND"  AS "products.brand",
                users."COUNTRY"  AS "users.country"
        FROM "PUBLIC"."ORDER_ITEMS"
             AS order_items
        LEFT JOIN "PUBLIC"."USERS"
             AS users ON (order_items."USER_ID") = (users."ID")
        LEFT JOIN "PUBLIC"."INVENTORY_ITEMS"
             AS inventory_items ON (order_items."INVENTORY_ITEM_ID") = (inventory_items."ID")
        LEFT JOIN "PUBLIC"."PRODUCTS"
             AS products ON (inventory_items."PRODUCT_ID") = (products."ID")
        LEFT JOIN "PUBLIC"."DISTRIBUTION_CENTERS"
             AS distribution_centers ON (products."DISTRIBUTION_CENTER_ID") = (distribution_centers."ID")

        GROUP BY 1,2,3,4,5
        ORDER BY 1
        LIMIT 500
    """

    test = ipe.parse_sql(sdk=sdk, qid=(777))
    expected_result = ["public.order_items", "public.inventory_items",
                       "public.products", "public.users", "public.distribution_centers"]
    assert isinstance(test, list)
    assert len(test) == 5
    assert sorted(test) == sorted(expected_result)


def test_get_view_path(mocker):
    response = ipe.get_view_path(project)
    assert len(response) == 18
    assert isinstance(response, dict)


def test_fetch_view_files():
    response = ipe.fetch_view_files(project)
    print(response)
    assert len(response) == 14
    assert isinstance(response, dict)
    assert response['kitten_order_items'] == [
        'kitten_order_items', 'users', 'kitten_users']


def test_get_sql_table_name():
    response = ipe.get_sql_table_name(project)
    expected_response = sql_table_names
    assert len(response) == 12
    assert isinstance(response, dict)


test_sql_table_name_data = {'foo': ['foo'], 'xbarr': ['barr']}


def test_get_sql_table_name_list():
    response = ipe.get_sql_table_name_list(test_sql_table_name_data, key=False)
    assert response == ['foo', 'barr']
    assert len(response) == 2
    assert isinstance(response, list)


def test_get_sql_from_elements(mocker):
    sdk = MockSDK()
    mocker.patch("lmanage.get_content_with_views.parse_sql")
    sql_table_name = ['public.order_items',
                      'public.inventory_items', 'public.users', 'public.products']
    lmanage.get_content_with_views.parse_sql.return_value = sql_table_name
    response = ipe.get_sql_from_elements(sdk, data)
    result = response[0]['sql_joins']
    assert isinstance(result, list)
    assert len(result) == 4
    assert result == sql_table_name


def test_get_dashboards(mocker):
    sdk = MockSDK()
    mocker.patch.object(sdk, "run_inline_query")
    sdk.run_inline_query.return_value = '''
    [
        {"dashboard.id":3,
        "dashboard_element.id":"4",
        "dashboard_element.type":"look",
        "dashboard_element.result_source":"taco",
        "query.model":"mackermodel",
        "query.view":"mackerview",
        "query.formatted_fields":"['orders','sales']",
        "query.id":"55",
        "dashboard.title":"franky fredericks",
        "look.id":"44"}]
    '''
    test = ipe.get_dashboards(sdk=sdk)
    assert isinstance(test, list)
    assert test[0]['dashboard.id'] == 3
    assert len(test[0]) == 10


def test_t_period_appearence(mocker):
    val = 'fliberrty.gibberty'
    test = ipe.test_period_appearence(val)
    assert test == True
    val2 = 'flivertygiverty'
    test2 = ipe.test_period_appearence(val2)
    assert test2 == False


def test_match_join_per_query(mocker):
    data = match_data
    test = ipe.match_join_per_query(data)
    assert isinstance(test, dict)
    assert len(test) == 7
    assert len(test['used_joins']) == 1
    assert isinstance(test['used_joins'], list)
    assert test['used_joins'] == ['`looker-private-demo.ecomm.order_items`']


def test_match_views_per_query(mocker):
    data = match_data
    data['used_joins'] = ['`looker-private-demo.ecomm.order_items`']
    test = ipe.match_views_per_query(data, project)
    print(test)
    assert test['sql_table_paths_'] == ['views/01_order_items.view.lkml']
    assert len(test) == 9
    assert len(test['used_view_names']) == 1
    assert isinstance(test['used_view_names'], list)
    assert test['used_view_names'] == ['order_items']


def test_find_unused_views(mocker):
    data = match_data
    data['used_view_names'] = ['order_items', 'test_ndt']
    test = ipe.find_unused_views(data)
    test_return = [
        'order_facts',
        'inventory_items',
        'users',
        'user_order_facts',
        'products',
        'repeat_purchase_facts',
        'distribution_centers'
    ]
    assert len(test['unused_joins']) == 7
    assert len(data['used_view_names']) == 2
    assert True if 'test_ndt' in data['used_view_names'] else False
    assert isinstance(test['unused_joins'], list)
    assert sorted(test_return) == sorted(test['unused_joins'])


# find_unused_view_data = {
#     'dashboard_id': 1,
#     'element_id': 1,
#     'sql_joins': ['`looker-private-demo.ecomm.order_items`'],
#     'fields_used': ["order_items.created_month", "order_items.count"],
#     'sql_table_name': ['`looker-private-demo.ecomm.distribution_centers`', '`looker-private-demo.ecomm.products`', '`looker-private-demo.ecomm.users`', '`looker-private-demo.ecomm.order_items`', '`looker-private-demo.ecomm.inventory_items`', '`looker-private-demo.ecomm.events`'],
#     'potential_join': ['events', 'sessions', 'session_landing_page', '<lookml.core.prop_string_unquoted object at 0x7f5b4b561f10>']
#     # 'potential_join': ['events', 'sessions', 'session_landing_page', < lookml.core.prop_string_unquoted object at 0x7f5b4b561f10 >, 'session_bounce_page', < lookml.core.prop_string_unquoted object at 0x7f5b4b572150 > , 'product_viewed', < lookml.core.prop_string_unquoted object at 0x7f5b4b572390 > , 'users', 'user_order_facts']
# }


# def test_find_unused_views_pylookml_reponses(mocker):
#     data = find_unused_view_data
#     data['used_view_names'] = ['order_items', 'test_ndt']
#     test = ipe.find_unused_views(data)
#     test_return = [
#         'order_facts',
#         'inventory_items',
#         'users',
#         'user_order_facts',
#         'products',
#         'repeat_purchase_facts',
#         'distribution_centers'
#     ]
#     assert len(test['unused_joins']) == 7
#     assert len(data['used_view_names']) == 1
#     assert True if 'test_ndt' in data['used_view_names'] else False
#     assert isinstance(test['unused_joins'], list)
#     assert sorted(test_return) == sorted(test['unused_joins'])

def test_match_view_to_dash():
    content_results = [{'dashboard.id': 1, 'dashboard_element.id': 1, 'dashboard_element.type': 'vis', 'dashboard_element.result_source': 'Lookless', 'query.model': 'bq', 'query.view': 'order_items',
                        'query.formatted_fields': '["order_items.created_month", "order_items.count"]', 'query.id': 59, 'dashboard.title': 'dash_1', 'look.id': None, 'sql_joins': ['`looker-private-demo.ecomm.order_items`']}]
    explore_results = ipe.fetch_view_files(project)
    sql_table_name = sql_table_names
    test = ipe.match_view_to_dash(content_results=content_results,
                                  explore_results=explore_results, sql_table_name=sql_table_name, proj=project)
    assert isinstance(test, list)
    assert len(test[0]) == 6
    assert isinstance(test[0]['fields_used'], str)
    assert test[0]['element_id'] == 1


path = './tests/snap_db_response.json'
with open(path) as f:
    client_data = ast.literal_eval(f.read())


def test_match_view_to_dash_extra_tests():
    client_results = client_data
    explore_results = ipe.fetch_view_files(project)
    sql_table_name = sql_table_names
    test = ipe.match_view_to_dash(content_results=client_results,
                                  explore_results=explore_results, sql_table_name=sql_table_name, proj=project)
    assert isinstance(test, list)
    assert len(test) == 9
