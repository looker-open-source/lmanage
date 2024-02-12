import logging
from looker_sdk.sdk.api40 import models
from os import name
import pytest
from lmanage.configurator.folder_configuration import create_folders as cf
from tests import fake_methods_data

input_data = fake_methods_data.input_data
LOGGER = logging.getLogger(__name__)


def test_create_folder(mocker):
    # Tests if there is a folder exists we raise an exception
    sdk = fake_methods_data.MockSDK()
    sf_data = fake_methods_data.MockCreateFolder(
        name='frankie_fish', parent_id='123')
    mocker.patch.object(sdk, "create_folder")
    sdk.create_folder.return_value = sf_data

    test = cf.CreateInstanceFolders(sdk=sdk, folder_metadata='5555').create_folder(
        folder_name='test', parent_id='123')
    assert isinstance(test, fake_methods_data.MockCreateFolder)
    assert test.name == 'frankie_fish'
    sdk.create_folder.assert_called_with(
        body=models.CreateFolder(name='test', parent_id='123'))
