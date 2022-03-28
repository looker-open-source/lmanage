from lmanage.utils import folder_config as fc
from unittest.mock import Mock
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
    def __init__(self, parent_id, folder_name):
        self.parent_id = parent_id
        self.folder_name = folder_name


class MockCreateFolder():
    def __init__(self, parent_id, folder_name):
        self.parent_id = parent_id
        self.folder_name = folder_name

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
    sf_data = MockSearchFolder(folder_name='goog', parent_id=2)
    mocker.patch.object(sdk, "search_folders")
    sdk.search_folders.return_value = [sf_data]

    with pytest.raises(Exception):
        fc.create_folder_if_not_exists(
            sdk=sdk, folder_name='googn', parent_id='4')


def test_create_folder_if_not_exists_parent1(mocker):
    # Tests if a folder has parent id of 1 we raise an exception
    sdk = MockSDK()
    sf_data = MockSearchFolder(folder_name='goog', parent_id=1)
    mocker.patch.object(sdk, "search_folders")
    sdk.search_folders.return_value = [sf_data]

    with pytest.raises(Exception):
        fc.create_folder_if_not_exists(
            sdk=sdk, folder_name='googn', parent_id='1')


@pytest.fixture
def mock_search_folder(mocker):
    sdk = MockSDK()
    sf_data = MockSearchFolder(folder_name='goog', parent_id=1)
    sf_data1 = MockSearchFolder(folder_name='gooli', parent_id=3)
    return mocker.patch.object(sdk, 'search_folders', side_effect=[sf_data, sf_data1])


def test_passphrase(mock_search_folder, mocker):
    # Tests the creation of a folder if it doesn't exist or have a parent id of 1
    sdk = MockSDK()
    cf_data = MockCreateFolder(parent_id=4, folder_name='googie')
    mock_search_folder.patch.object(sdk, "search_folders")
    mocker.patch.object(sdk, "create_folder")

    sdk.create_folder.return_value = [cf_data]

    test = fc.create_folder_if_not_exists(
        sdk=sdk, folder_name='googn', parent_id='4')
    assert isinstance(test, list)
