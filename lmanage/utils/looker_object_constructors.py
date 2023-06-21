import ruamel.yaml


yaml = ruamel.yaml.YAML()


@yaml.register_class
class LookerFolder():
    def __init__(self, id, folder_metadata, access_list):
        self.parent_id = folder_metadata.get('parent_id')
        self.id = id
        self.name = folder_metadata.get('name')
        self.subfolder = []
        self.content_metadata_id = folder_metadata.get('content_metadata_id')
        self.team_edit = self.breakup_access_list(
            access_list=access_list, access_type='edit')
        self.team_view = self.breakup_access_list(
            access_list=access_list, access_type='view')

    def add_child_folder(self, ref):
        self.subfolder.append(ref)

    def breakup_access_list(self, access_list, access_type):
        response = []
        for access in access_list:
            team = access.get(access_type, None)
            if team is not None:
                response.append(team)
        return response


class LookerPermissionSet():
    def __init__(self, permissions, name):
        self.permissions = permissions
        self.name = name


class LookerUserAttribute():
    def __init__(self, teams_val: dict, name: str, uatype: bool, hidden_value: bool, user_view, user_edit, default_value) -> object:
        self.name = name
        self.uatype = uatype
        self.hidden_value = hidden_value
        self.user_view = str(user_view)
        self.user_edit = str(user_edit)
        self.default_value = default_value
        self.teams = teams_val


class LookerModelSet():
    def __init__(self, models, name):
        self.models = models
        self.name = name


class LookerRoles():
    def __init__(self, permission_set, model_set, teams, name):
        self.permission_set = permission_set
        self.model_set = model_set
        self.teams = teams
        self.name = name


class LookerGroup():
    def __init__(self, id, group_metadata):
        self.name = group_metadata.name
        self.id = id
        self.children = []


class LookObject():
    def __init__(self, description, query_obj, title, legacy_folder_id, look_id, schedule_plans):
        self.legacy_folder_id = legacy_folder_id
        self.look_id = look_id
        self.title = title
        self.query_obj = query_obj
        self.description = description
        self.schedule_plans = schedule_plans


class DashboardObject():
    def __init__(self, legacy_folder_id, lookml, dashboard_id, dashboard_slug, schedule_plans) -> None:
        self.legacy_folder_id = legacy_folder_id
        self.lookml = lookml
        self.dashboard_id = dashboard_id
        self.dashboard_slug = dashboard_slug
        self.schedule_plans = schedule_plans


class BoardObject():
    def __init__(self, content_metadata_id, section_order, title, primary_homepage, board_sections, description) -> None:
        self.content_metadata_id = content_metadata_id
        self.section_order = section_order
        self.title = title
        self.primary_homepage = primary_homepage
        self.board_sections = board_sections
        self.description = description
