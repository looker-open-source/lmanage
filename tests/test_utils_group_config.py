from os import name, walk
from looker_sdk import models
import looker_sdk
from lmanage.utils import group_config as gc
import pytest

input_data = {'role_BusinessOperations_Developer':
              {'role': 'BODevelopers',
               'permissions': ['access_data', 'use_sql_runner'],
               'model_set': [{'name': 'lk1_test_set', 'models': ['test', 'test2']}],
               'team': ['BusinessOperations_BO_Dev']},
              'folder_permissions':
              {'business_operations_folder': [
                  {'name': 'Business Operations',
                   'team_view': ['Snaptest'],
                   'subfolder': [{'name': 'test_sub', 'team_edit': ['Freddy'], 'team_view': ['hugo']},
                                 {'name': 'test_sub2',
                                  'subfolder':
                                  [{'name': 'test_sub_sub',
                                    'team_edit': ['Famke'],
                                    'team_view': ['hugle']},
                                   {'name': 'subdiddy',
                                    'subfolder': [{'name': 'hugle_testy', 'team_edit': ['Freddy'], 'team_view': ['hugle']}]}]}]}],

               'ua_region_all':
               {'name': 'region_all',
                'type': 'string',
                'hidden_value': 'false',
                'user_view': 'true',
                'user_edit': 'false',
                'value': ['us', 'ag', 'bb', 'dd'],
                'team': ['Cameos', 'Freddy', 'AudreyGroup']}}}


class MockSDK():
    def search_groups(self):
        pass

    def create_group(self):
        pass


class MockSearchGroup():
    def __init__(self, group_name):
        self.group_name = group_name


class MockCreateFolder():
    def __init__(self, id, name, content_metadata_id):
        self.id = id
        self.name = name
        self.content_metadata_id = content_metadata_id


def test_get_unique_groups():
    yaml = input_data
    folder_data = [[{
        'team_edit': ['test_edit_group'],
        'team_view': ['test_view_group']
    }]]

    test = gc.get_unique_groups(parsed_yaml=yaml, yaml_folders=folder_data)
    assert isinstance(test, list)
    assert 'test_edit_group' in test
    assert 'test_view_group' in test
    assert len(test) == 3
    assert 'BusinessOperations_BO_Dev' in test


def test_create_group_if_exists(mocker):
    sdk = MockSDK()
    mocker.patch.object(sdk, 'search_groups')
    gdata = MockSearchGroup(group_name='foo')
    sdk.search_groups.return_value = gdata
    with pytest.raises(Exception):
        gc.create_group_if_not_exists(
            sdk=sdk,
            group_name='test'
        )


def test_create_group_if_not_exists(mocker):
    sdk = MockSDK()
    mocker.patch.object(sdk, 'search_groups')
    sdk.search_groups.return_value = None
    mocker.patch.object(sdk, 'create_group')
    gc.create_group_if_not_exists(
        sdk=sdk,
        group_name='olivia'
    )
    sdk.create_group.assert_called_with(
        body=looker_sdk.models.WriteGroup(
            name='olivia',
            can_add_to_content_metadata=True)
    )
