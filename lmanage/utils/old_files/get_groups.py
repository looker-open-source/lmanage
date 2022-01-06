import logging
import coloredlogs
from looker_sdk import models
import looker_sdk
import parse_yaml

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')
path = '/usr/local/google/home/hugoselbie/code_sample/py/lmanage/tests/example_yamls/fullinstance.yaml'
data = parse_yaml.Yaml(yaml_path=path)
dd = data.read_provision_yaml()


def get_unique_folders(
        sdk: looker_sdk,
        parsed_yaml: dict) -> list:

    folder_metadata = []
    for k, v in parsed_yaml.items():
        if 'folder' in k:
            temp = {}
            folder_name = parsed_yaml['folder']['name']

            try:
                folder = sdk.create_folder(
                    body=models.Folder(
                        name=folder_name,
                        parent_id=1
                    )
                )
                temp['folder_id'] = folder.id
                temp['content_metadata_id'] = folder.content_metadata_id
            except looker_sdk.error.SDKError:
                logger.info('folder has already been created')
                folder = sdk.search_folders(name=folder_name)
                temp['folder_id'] = folder[0]['id']
                temp['content_metadata_id'] = folder[0]['content_metadata_id']
            folder_metadata.append(temp)
    return folder_metadata


x = get_unique_folders(sdk=sdk, parsed_yaml=dd)
print(x)
