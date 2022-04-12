from looker_sdk import models, error
import logging
from lmanage.create_user_permissions import user_permission as up
from tests import fake_methods_data

input_data = fake_methods_data.input_data
LOGGER = logging.getLogger(__name__)


def test_get_role_metadata():
    # Tests how the input of the yaml file
    test = up.get_role_metadata(parsed_yaml=input_data)
    print(test)
    assert len(test[0]) == 4
    assert test[0].get('role_name') == 'BODevelopers'
    assert isinstance(test, list)


def test_create_permission_set(mocker):
    sdk = fake_methods_data.MockSDK()
    mocker.patch.object(sdk, 'create_permission_set',
                        side_effect=error.SDKError("permission set error"))
    mocker.patch.object(sdk, 'search_permission_sets')
    mocker.patch.object(sdk, 'update_permission_set')

    up.create_permission_set(
        sdk=sdk, permission_set_list=fake_methods_data.fake_permission_set)
    sdk.create_permission_set.assert_called_with(
        body=models.WritePermissionSet(
            name='bodevelopers',
            permissions=['access_data', 'use_sql_runner'])
    )
