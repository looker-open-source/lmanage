from lmanage import validate_content
import pandas as pd
import lmanage


class MockSDK():
    def all_spaces():
        pass

    def content_validation():
        pass

    def scheduled_plan_run_once():
        pass


class MockSpaceBase():
    def __init__(self, id, parent_id, name):
        self.id = id
        self.parent_id = parent_id
        self.name = name


class MockContentValidationError():
    def __init__(self, message, field_name, model_name, explore_name):
        self.message = message
        self.field_name = field_name
        self.model_name = model_name
        self.explore_name = explore_name


class MockContentValidationLook():
    def __init__(self, id, title, folder, space, errors):
        self.id = id
        self.title = title
        self.folder = folder
        self.space = space
        self.errors = errors


class MockContentValidationDashboard():
    def __init__(self, id, title, folder, space, dashboard_element):
        self.id = id
        self.title = title
        self.folder = folder
        self.space = space
        self.dashboard_element = dashboard_element


class MockContentValidationDashboardElement():
    def __init__(self, id, dashboard_id, look_id):
        self.id = id
        self.dashboard_id = dashboard_id
        self.look_id = look_id


class MockContentValidationFolder():
    def __init__(self, name, id):
        self.name = name
        self.id = id


class MockContentValidationSpace():
    def __init__(self, name, id):
        self.name = name
        self.id = id


class MockContentValidatorError():
    def __init__(self, look, title, folder, space, dashboard):
        self.look = look
        self.title = title
        self.folder = folder
        self.space = space
        self.dashboard = dashboard


class MockContentValidation():
    def __init__(self, content_with_errors):
        self.content_with_errors = content_with_errors


def test_get_space_data(mocker):
    sdk = MockSDK()
    mocker.patch.object(sdk, "all_spaces")
    sdk.all_spaces.return_value = MockSpaceBase(
        id="5",
        parent_id="3",
        name="spacey"
    )

    test = validate_content.get_space_data(sdk=sdk)
    assert isinstance(test, MockSpaceBase)
    assert test.id == "5"
    assert test.name == "spacey"


def test_parse_broken_content(mocker):
    sdk = MockSDK()
    mocker.patch.object(sdk, "content_validation")
    lookerror = MockContentValidationError(
        look=MockContentValidationLook(
            id="1",
            title="test_title",
            folder=MockContentValidationFolder(
                name="hugo",
                id="555"
            ),
            space=MockContentValidationSpace(
                name="spaceyhugo",
                id="556"
            ),
            errors=[
                MockContentValidationError(
                    message="missing model",
                    field_name="missing field",
                    model_name="model",
                    explore_name="explore"
                )
            ]
        )
    )
    dasherror = MockContentValidationError(
        dashboard=MockContentValidationDashboard(
            id="55",
            folder=MockContentValidationFolder(
                name="hugo",
                id="555"
            ),
            space=MockContentValidationSpace(
                name="spaceyhugo",
                id="556"
            ),
            title="test_title_dash",
            dashboard_element=MockContentValidationDashboardElement(
                look_id="5",
                id="44",
                dashboard_id="55"
            )
        )
    )
    content_validation_x = MockContentValidation(
        content_with_errors=[
            dasherror, lookerror
        ]
    )
    sdk.content_validation.return_value = content_validation


def test_send_content_once(mocker):
