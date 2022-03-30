from os import name
from looker_sdk import models
from lmanage.utils import folder_config as fc
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
    def search_folders(self):
        pass

    def create_folder(self):
        pass


class MockSearchFolder():
    def __init__(self, parent_id, name, id):
        self.parent_id = parent_id
        self.name = name
        self.id = id


class MockCreateFolder():
    def __init__(self, id, name, content_metadata_id):
        self.id = id
        self.name = name
        self.content_metadata_id = content_metadata_id

# Tests how the input of the yaml file


def test_get_folder_metadata():
    # Tests how the input of the yaml file
    test = fc.get_folder_metadata(parsed_yaml=input_data)
    assert len(test[0]) == 6
    assert test[0][0]['name'] == 'Business Operations'
    assert isinstance(test, list)


def test_create_folder_ifexists(mocker):
    # Tests if there is a folder exists we raise an exception
    sdk = MockSDK()
    sf_data = MockSearchFolder(name='goog', parent_id=2, id=3)
    mocker.patch.object(sdk, "search_folders")
    sdk.search_folders.return_value = [sf_data]

    with pytest.raises(Exception):
        fc.create_folder_if_not_exists(
            sdk=sdk, folder_name='googn', parent_folder_name='test')


def test_create_folder_if_not_exists_parent1(mocker):
    # Tests if a folder has parent id of 1 we raise an exception
    sdk = MockSDK()
    sf_data = MockSearchFolder(name='goog', parent_id=1, id=3)
    mocker.patch.object(sdk, "search_folders")
    sdk.search_folders.return_value = [sf_data]

    with pytest.raises(Exception):
        fc.create_folder_if_not_exists(
            sdk=sdk, folder_name='googn', parent_folder_name='1')


def test_create_folder_if_not_exists_xyz(mocker):
    # Tests the creation of a folder if it doesn't exist or have a parent id of 1
    sdk = MockSDK()
    sf_data = None
    sf_data1 = [MockSearchFolder(name='frank', parent_id=4, id=55)]
    mocker.patch.object(sdk, 'search_folders', side_effect=[sf_data, sf_data1])
    mocker.patch.object(sdk, 'create_folder')

    fc.create_folder_if_not_exists(
        sdk=sdk, folder_name='frankie fish', parent_folder_name='4')
    sdk.create_folder.assert_called_with(
        body=models.CreateFolder(name='frankie fish', parent_id=55))


def test_create_looker_folder_metadata(mocker):
    # Tests the creation of a folder if it doesn't exist or have a parent id of 1
    input_data = [[
        {'name': 'Business Operations',
         'parent_id': '1',
         'team_edit': ['test1'],
         'team_view': ['test2']}]]
    mocker.patch('lmanage.utils.folder_config.create_folder_if_not_exists')
    data = MockCreateFolder(
        id=3,
        name='Frankie',
        content_metadata_id=3
    )
    fc.create_folder_if_not_exists.return_value = data
    test = fc.create_looker_folder_metadata(
        sdk='false', unique_folder_list=input_data)

    assert isinstance(test, list)
    assert test[0].get('folder_id') == 3
    assert isinstance(test[0].get('team_edit'), list)
    assert test[0].get('folder_name') == 'Frankie'
