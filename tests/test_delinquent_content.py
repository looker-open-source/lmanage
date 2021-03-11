from lmanage import delinquent_content
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
    [{"content_usage.last_accessed_date": "2021-02-16",
      "content_usage.content_id": "5",
      "content_usage.content_title": "5",
      "content_usage.content_type": "look"
                                      },
                                         {
        "content_usage.last_accessed_date": "2021-02-13",
        "content_usage.content_id": "2",
        "content_usage.content_title": "2",
        "content_usage.content_type": "dashboard"
    },
        {
        "content_usage.last_accessed_date": "2021-02-11",
        "content_usage.content_id": "1",
        "content_usage.content_title": "test",
        "content_usage.content_type": "look"
    }
    ]
    '''
    test = delinquent_content.get_last_accessed_content_dates(
        content_type="test", delinquent_days=5, sdk=sdk)

    assert isinstance(test, list)


def test_delinquent_content(mocker):
    mocker.patch("delinquent_content.get_last_accessed_content_dates")
    delinquent_content.get_last_accessed_content_dates.return_value = [{"content_usage.last_accessed_date": "2021-02-16",
                                                                        "content_usage.content_id": "5",
                                                                        "content_usage.content_title": "5",
                                                                        "content_usage.content_type": "look"
                                                                        },
                                                                       {
        "content_usage.last_accessed_date": "2021-02-13",
        "content_usage.content_id": "2",
        "content_usage.content_title": "2",
        "content_usage.content_type": "dashboard"
    },
        {
        "content_usage.last_accessed_date": "2021-02-11",
        "content_usage.content_id": "1",
        "content_usage.content_title": "test",
        "content_usage.content_type": "look"
    }
    ]
    mocker.patch("subprocess.run")
