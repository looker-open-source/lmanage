from lmanage import getContentWithViews
import pandas as pd
import lmanage


class MockSDK():
    def run_inline_query():
        pass


class MockQuery():
    def __init__(self, fields, query_id):
        self.fields = fields
        self.query_id = query_id


class MockSQL():
    def __init__(self, sql):
        self.sql = sql


def test_parse_sql_bq(mocker):
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

    test = getContentWithViews.parse_sql(sdk=sdk, qid=(777))
    expected_result = ["order_items", "inventory_items",
                       "products", "users", "distribution_centers"]
    assert isinstance(test, list)
    assert len(test) == 5
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

    test = getContentWithViews.parse_sql(sdk=sdk, qid=(777))
    expected_result = ["order_items", "inventory_items",
                       "products", "users", "distribution_centers"]
    assert isinstance(test, list)
    assert len(test) == 5
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

    test = getContentWithViews.parse_sql(sdk=sdk, qid=(777))
    expected_result = ["order_items", "inventory_items",
                       "products", "users", "distribution_centers"]
    assert isinstance(test, list)
    assert len(test) == 5
    assert sorted(test) == sorted(expected_result)


def test_get_content_id_title(mocker):
    sdk = MockSDK()
    mocker.patch.object(sdk, "all_dashboards")
    mocker.patch.object(sdk, "all_looks")

    dash = MockDashboard("1", "test_dash", "dashboard")
    look = MockLook("test_title", "5", "look", "5")
    sdk.all_dashboards.return_value = [dash]
    sdk.all_looks.return_value = [look]

    content_list = getContentWithViews.get_content_id_title(sdk=sdk)
    expected_element_look = {"id": "1",
                             "title": "test_title", "content_type": "look"}
    expected_element_dashboard = {
        "id": "1", "title": "test_dash", "content_type": "dashboard"}

    expected_result = [sorted(expected_element_dashboard),
                       sorted(expected_element_look)]

    assert isinstance(content_list, list)


def test_find_content_views(mocker):
    sdk = MockSDK()
    mocker.patch.object(sdk, "dashboard_dashboard_elements")
    mocker.patch.object(sdk, "look")
    mocker.patch("lmanage.getContentWithViews.parse_sql")
    mocker.patch("lmanage.getContentWithViews.get_content_id_title")

    views = ["order_items", "inventory_items",
             "products", "users", "distribution_centers"]
    element_look = {"id": "1",
                    "title": "test_title", "content_type": "look", "query_id": "5"}
    element_dashboard = {
        "id": "1", "title": "test_dash", "content_type": "dashboard"}
    look = MockLook("test_title", "5", "look", "5")
    dash_elem = MockDashboardElement("4", "7", "12", "mrmacpherson", [
                                     "order_items", "test_tables"], "1")
    dash_elem_1 = MockDashboardElement("8", "2", "4", "mrmacpherson1", [
        "order_items", "test_tables1"], "12")

    result = [element_dashboard,
              element_look]

    lmanage.getContentWithViews.parse_sql.return_value = views
    lmanage.getContentWithViews.get_content_id_title.return_value = result
    sdk.dashboard_dashboard_elements.return_value = [dash_elem, dash_elem_1]
    sdk.look.return_value = look

    content_view_list = getContentWithViews.find_content_views(
        sdk=sdk, looker_content=getContentWithViews.get_content_id_title(sdk=sdk))
    assert isinstance(content_view_list, list)
