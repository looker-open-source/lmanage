import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')
logging.getLogger("looker_sdk").setLevel(logging.WARNING)


class LookerFolder():
    def __init__(self, sdk, id):
        self.sdk = sdk
        self.folder_metadata = self.get_folder_metadata(folder_id=str(id))
        self.name = self.folder_metadata.name
        self.parent_id = self.folder_metadata.parent_id
        self.id = id
        self.children = []
        self.content_metadata_id = self.folder_metadata.content_metadata_id
        self.content_access_list = self.get_content_access_metadata(
            folder_id=id)

    def get_folder_metadata(self, folder_id):
        f_metadata = self.sdk.folder(folder_id=str(folder_id))
        return f_metadata

    def get_content_access_metadata(self, folder_id):
        r = []
        cmi_metadata = self.sdk.response = self.sdk.all_content_metadata_accesses(
            content_metadata_id=169)
        for cmi in cmi_metadata:
            group_id = cmi.group_id
            permission_type = cmi.permission_type
            temp = {}
            temp[permission_type] = LookerGroup(sdk=self.sdk, id=group_id).name
            r.append(temp)
        logger.info(f'added content_access_list for folder {folder_id}')

        return r

    def create_name(self, folder_id):
        return self.sdk.folder(folder_id=str(folder_id)).name

    def add_child(self, sid):
        f_object = LookerFolder(sdk=self.sdk, id=sid)
        self.children.append(f_object)

    def add_child_folder(self, ref):
        self.children.append(ref)


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
