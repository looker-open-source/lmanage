from os import name, walk
from looker_sdk import models
import looker_sdk
from utils import group_config as gc
import pytest
from lmanage.tests import fake_methods_data

input_data = fake_methods_data.input_data


def test_get_unique_groups():
    # Test to determine if unique groups are taken out for creation of the input_data
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
    # Test to determine if there is an existing group an exception is raised
    sdk = fake_methods_data.MockSDK()
    mocker.patch.object(sdk, 'search_groups')
    gdata = fake_methods_data.MockSearchGroup(group_name='foo')
    sdk.search_groups.return_value = gdata
    with pytest.raises(Exception):
        gc.create_group_if_not_exists(
            sdk=sdk,
            group_name='test'
        )


def test_create_group_if_not_exists(mocker):
    # Test to determine if there isn't a group the make group call is created with the appropriate parameters
    sdk = fake_methods_data.MockSDK()
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


def test_get_group_metadata(mocker):
    gc_data = fake_methods_data.MockCreateGroup(id=4, name='karen')
    gc_data1 = fake_methods_data.MockCreateGroup(id=5, name='jimmy')
    mock_folder_list = ['frankiefish', 'tommy']
    mocker.patch('utils.group_config.create_group_if_not_exists',
                 side_effect=[gc_data, gc_data1])

    gc.create_group_if_not_exists.return_value = gc_data

    test = gc.get_group_metadata(sdk=sdk, unique_group_list=mock_folder_list)

    assert isinstance(test, list)
    assert test[0].get('group_id') == 4
    assert test[1].get('group_name') == 'jimmy'
