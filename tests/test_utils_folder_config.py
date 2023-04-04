import logging
from os import name
from looker_sdk import models
import looker_sdk
from looker_sdk import error
#from lmanage.utils import folder_config as fc
import pytest
from tests import fake_methods_data
from lmanage.capturator.folder_capturation.folder_config import CaptureFolderConfig
input_data = fake_methods_data.input_data
LOGGER = logging.getLogger(__name__)

def test_get_all_folders(mocker):
    expected_response = ['1', '2', '3', '6', '7']
    # Mock SDK method to return instance folders
    sdk = fake_methods_data.MockSDK()
    mocker.patch.object(sdk, "all_folders")
    data1 = fake_methods_data.MockAllFolder(id='1', parent_id=None)
    data2 = fake_methods_data.MockAllFolder(id='2', parent_id=None)
    data3 = fake_methods_data.MockAllFolder(id='3', parent_id=None)
    data4 = fake_methods_data.MockAllFolder(id='4', parent_id='2')
    data5 = fake_methods_data.MockAllFolder(id='5', parent_id='3')
    data6 = fake_methods_data.MockAllFolder(id='6', parent_id='1')
    data7 = fake_methods_data.MockAllFolder(id='7', parent_id='4')
    sdk.all_folders.return_value = [
        data1,
        data2,
        data3,
        data4,
        data5,
        data6,
        data7
    ]
    test = CaptureFolderConfig(sdk=sdk).get_all_folders()
    assert test == expected_response

def test_clean_folders():
    sdk = fake_methods_data.MockSDK()
    folder_list = ['1', '2', '3', '4',  'lookml', '5', '6','7',None]
    expected_response = ['7','6']
    result = CaptureFolderConfig(sdk=sdk).clean_folders(folder_list)
    assert expected_response == result

def test_get_content_access_metadata(mocker):
    #test root folder first
    sdk = fake_methods_data.MockSDK()

    mocker.patch.object(sdk,'all_content_metadata_accesses')
    sdk.all_content_metadata_accesses.return_value = [
        fake_methods_data.Mock_get_content_access_metadata('view', None),
        fake_methods_data.Mock_get_content_access_metadata('edit', None),
        fake_methods_data.Mock_get_content_access_metadata('edit', 1),
        fake_methods_data.Mock_get_content_access_metadata('view', 1)
    ]

    mocker.patch.object(sdk,'group')
    sdk.group.return_value = fake_methods_data.MockObj.obj_return("All Folders")
    cmi = '1'
    result = CaptureFolderConfig(sdk=sdk).get_content_access_metadata(cmi, True)
    assert result == [{'edit': 'All Folders'}, {'view': 'All Folders'}]

    #test other folder
    mocker.patch.object(sdk,'all_content_metadata_accesses')
    sdk.all_content_metadata_accesses.return_value = [
        fake_methods_data.Mock_get_content_access_metadata('view', None),
        fake_methods_data.Mock_get_content_access_metadata('edit', None),
        fake_methods_data.Mock_get_content_access_metadata('edit', 1),
        fake_methods_data.Mock_get_content_access_metadata('view', 1)
    ]

    mocker.patch.object(sdk,'group')
    sdk.group.return_value = fake_methods_data.MockObj.obj_return("Joe Test Folder")
    cmi = '6'
    result = CaptureFolderConfig(sdk=sdk).get_content_access_metadata(cmi, False)
    assert result == [{'edit': 'Joe Test Folder'}, {'view': 'Joe Test Folder'}]

def test_create_folder_objects(mocker):
    pass