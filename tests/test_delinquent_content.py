from lmanage import delinquent_user
import subprocess
import pandas as pd
import lmanage


class MockSDK():
    def run_query():
        pass

    def all_dashboards():
        pass

    def all_looks():
        pass

    def dashboard_dashboard_elements():
        pass

    def look():
        pass

    def run_inline_query():
        pass

# create mock dashboard elements


class MockQuery():
    def __init__(self, fields, filters, limit):
        self.fields = fields
        self.filters = filters
        self.limit = limit


class MockSQL():
    def __init__(self, sql):
        self.sql = sql


class MockLook():
    def __init__(self, title, look_id, content_type, query_id):
        self.title = title
        self.id = look_id
        self.content_type = content_type
        self.query_id = query_id


class MockDashboard():
    def __init__(self, dash_id, title, content_type):
        self.id = dash_id
        self.title = title
        self.content_type = content_type


class MockDashboardElement():
    def __init__(self, query_id, id, dashboard_id, title, tables, look):
        self.id = id
        self.query_id = query_id
        self.dashboard_id = dashboard_id
        self.title = title
        self.tables = tables
        self.look = look


def test_get_last_accessed_content_dates(mocker):
    sdk = MockSDK()
    mocker.patch.object(sdk, "run_inline_query")
    sdk.run_inline_query.return_value = '''
   [{"user.id":3,"user.name":"aa aa","user.created_date":"2021-02-17","user_facts.last_ui_login_date":null,"user_facts.last_ui_login_credential_type":null,"days_since_last_login":null,"history.most_recent_query_date":"2021-03-05","no_query_login":"No"},
{"user.id":4,"user.name":"hugo test","user.created_date":"2021-02-17","user_facts.last_ui_login_date":null,"user_facts.last_ui_login_credential_type":null,"days_since_last_login":null,"history.most_recent_query_date":"2021-03-03","no_query_login":"No"},
{"user.id":1,"user.name":"Hugo Selbie","user.created_date":"2021-02-05","user_facts.last_ui_login_date":"2021-03-08","user_facts.last_ui_login_credential_type":"email","days_since_last_login":4,"history.most_recent_query_date":"2021-03"}]

    '''
    test = delinquent_user.find_delinquent_users(sdk=sdk, delinquent_days=2)
    assert isinstance(test, list)
