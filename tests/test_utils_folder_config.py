import logging
from os import name
from looker_sdk import models
import looker_sdk
from looker_sdk import error
from utils import folder_config as fc
import pytest
from lmanage.tests import fake_methods_data

input_data = fake_methods_data.input_data
LOGGER = logging.getLogger(__name__)


def test_get_folder_metadata():
    # Tests how the input of the yaml file
    test = fc.get_folder_metadata(parsed_yaml=input_data)
    assert len(test[0]) == 6
    assert test[0][0]['name'] == 'Business Operations'
    assert isinstance(test, list)


def test_create_folder_if_not_exists(mocker):
    # Tests if there is a folder exists we raise an exception
    sdk = fake_methods_data.MockSDK()
    sf_data = fake_methods_data.MockSearchFolder(
        name='goog', parent_id=2, id=3)
    cf_data = fake_methods_data.MockCreateGroup(id=3, name='dddd')
    mocker.patch.object(sdk, "search_folders")
    mocker.patch.object(sdk, "create_folder")
    sdk.search_folders.return_value = [sf_data]
    sdk.create_folder.return_value = [cf_data]
    test = fc.create_folder_if_not_exists(
        sdk=sdk, folder_name='frankie fish', parent_folder_name='test')
    print(type(test[0]))
    assert isinstance(test, list)
    sdk.create_folder.assert_called_with(
        body=models.CreateFolder(name='frankie fish', parent_id=3))


def test_create_folder_if_not_exists_parent1(mocker, caplog):
    # Tests if a folder has parent id of 1 we log a message
    caplog.set_level(logging.WARNING)
    sdk = fake_methods_data.MockSDK()
    sf_data = fake_methods_data.MockSearchFolder(
        name='goog', parent_id=1, id=3)
    mocker.patch.object(sdk, "search_folders")
    mocker.patch.object(sdk, "create_folder",
                        side_effect=error.SDKError("test_error"))
    sdk.search_folders.return_value = [sf_data]
    fc.create_folder_if_not_exists(
        sdk=sdk, folder_name='googn', parent_folder_name='1')

    assert 'Folder googn is a reserved top level folder' in caplog.text


def test_create_folder_error_if_exists(mocker, caplog):
    # Tests the creation of a folder if it doesn't exist or have a parent id of 1
    caplog.set_level(logging.WARNING)
    sdk = fake_methods_data.MockSDK()
    sf_data = fake_methods_data.MockSearchFolder(
        name='goog', parent_id=1, id=3)
    mocker.patch.object(sdk, "search_folders")
    mocker.patch.object(sdk, "create_folder",
                        side_effect=error.SDKError("logger error captured"))
    sdk.search_folders.return_value = [sf_data]
    fc.create_folder_if_not_exists(
        sdk=sdk, folder_name='googn', parent_folder_name='2')
    assert 'logger error captured' in caplog.text


def test_create_looker_folder_metadata(mocker):
    # Tests the creation of a folder if it doesn't exist or have a parent id of 1
    input_data = [[
        {'name': 'Business Operations',
         'parent_id': '1',
         'team_edit': ['test1'],
         'team_view': ['test2']}]]
    mocker.patch('utils.folder_config.create_folder_if_not_exists')
    data = fake_methods_data.MockCreateFolder(
        id=3,
        name='Frankie',
        content_metadata_id=3
    )
    fc.create_folder_if_not_exists.return_value = data
    test = fc.create_looker_folder_metadata(
        sdk='false', unique_folder_list=input_data)

    assert isinstance(test, list)
    assert test[0].get('folder_id') == 3
