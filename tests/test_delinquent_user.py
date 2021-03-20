from lmanage import delinquent_user
import json
import subprocess
import pandas as pd
import lmanage


class MockSDK():
    def user():
        pass

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


class MockUser():
    def __init__(self, id, is_disabled):
        self.id = id
        self.is_disabled = is_disabled


def test_get_user_list(mocker):
    sdk = MockSDK()
    mocker.patch.object(sdk, "run_inline_query")
    sdk.run_inline_query.return_value = '''
   [
        {"user.id":3,
        "user.name":"aa aa",
        "user.created_date":"2021-02-17",
        "user_facts.last_ui_login_date":null,
        "user_facts.last_ui_login_credential_type":null,
        "days_since_last_login":null,
        "history.most_recent_query_date":"2021-03-05",
        "no_query_login":"No"},

        {"user.id":4,
        "user.name":"hugo test",
        "user.created_date":"2021-02-17",
        "user_facts.last_ui_login_date":null,
        "user_facts.last_ui_login_credential_type":null,
        "days_since_last_login":null,
        "history.most_recent_query_date":"2021-03-03",
        "no_query_login":"No"},

        {"user.id":1,
        "user.name":"Hugo Selbie",
        "user.created_date":"2021-02-05",
        "user_facts.last_ui_login_date":"2021-03-08",
        "user_facts.last_ui_login_credential_type":"email",
        "days_since_last_login":4,
        "history.most_recent_query_date":"2021-03"}]

    '''
    test = delinquent_user.get_user_list(sdk=sdk)
    assert isinstance(test, list)
    assert len(test) == 3


def test_find_delinquent_users(mocker):
    sdk = MockSDK()
    mocker.patch("lmanage.delinquent_user.get_user_list")
    lmanage.delinquent_user.get_user_list.return_value = '''
   [
        {"user.id":3,
        "user.name":"aa aa",
        "user.created_date":"2021-02-17",
        "user_facts.last_ui_login_date":null,
        "user_facts.last_ui_login_credential_type":null,
        "days_since_last_login":null,
        "history.most_recent_query_date":"2021-03-05",
        "no_query_login":"No"},

        {"user.id":4,
        "user.name":"hugo test",
        "user.created_date":"2021-02-17",
        "user_facts.last_ui_login_date":null,
        "user_facts.last_ui_login_credential_type":null,
        "days_since_last_login":null,
        "history.most_recent_query_date":"2021-03-03",
        "no_query_login":"No"},

        {"user.id":1,
        "user.name":"Hugo Selbie",
        "user.created_date":"2021-02-05",
        "user_facts.last_ui_login_date":"2021-03-08",
        "user_facts.last_ui_login_credential_type":"email",
        "days_since_last_login":4,
        "history.most_recent_query_date":"2021-03"}]

    '''
    test = delinquent_user.find_delinquent_users(sdk=sdk, delinquent_days=2)
    assert isinstance(test, list)
    assert len(test) == 1


def test_disable_delinquent_users(mocker):
    test_list = [1, 2]

    sdk = MockSDK()
    mocker.patch.object(sdk, "user")
    sdk.user.return_value = MockUser(
        id="1",
        is_disabled="False"
    )
    test = delinquent_user.disable_deliquent_users(
        user_list=test_list, sdk=sdk)
    assert isinstance(test, list)
