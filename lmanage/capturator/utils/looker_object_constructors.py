import logging
import coloredlogs
import ruamel.yaml

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')
logging.getLogger("looker_sdk").setLevel(logging.WARNING)

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


class LookerGroup():
    def __init__(self, sdk, id):
        self.sdk = sdk
        self.group_metadata = self.get_group_metadata(group_id=id)
        self.name = self.group_metadata.name
        self.id = id
        self.children = []

    def get_group_metadata(self, group_id):
        g_metadata = self.sdk.group(group_id=group_id)
        return g_metadata

    def create_name(self, folder_id):
        return self.sdk.folder(folder_id=str(folder_id)).name

    def add_child(self, sid):
        f_object = LookerFolder(sdk=self.sdk, id=sid)
        self.children.append(f_object)
