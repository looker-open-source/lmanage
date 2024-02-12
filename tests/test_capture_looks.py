import logging
from os import name
import pytest
from lmanage.capturator.content_capturation import look_capture as lc
from tests import fake_methods_data

input_data = fake_methods_data.input_data


def test_get_all_looks_metadata(mocker):
    sdk = fake_methods_data.MockSDK()
    look_obj = lc.LookCapture(sdk=sdk, content_folders=123)
    all_look_data = fake_methods_data.MockAll_look_Response(
        id='123', folder='123')
    mocker.patch.object(sdk, "all_looks")
    sdk.all_looks.return_value = all_look_data
    response = [look_obj.get_all_looks_metadata()]

    assert isinstance(response, list)
    assert 'id' in response[0]
    assert 'folder' in response[0]
