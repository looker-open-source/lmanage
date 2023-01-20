import logging
import coloredlogs
import looker_sdk
from lmanage.configurator.user_attribute_configuration import create_ua_permissions as cuap
from lmanage.configurator.folder_configuration import folder_config as fc
from lmanage.configurator.folder_configuration import create_folder_permissions as cfp
from lmanage.configurator.folder_configuration import create_folders as cf
from lmanage.configurator.user_group_configuration import role_config as rc
from lmanage.configurator.user_group_configuration import group_config as gc
from lmanage.configurator.user_group_configuration import user_permission as up
from lmanage.utils import parse_yaml as py


logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')
logging.getLogger("looker_sdk").setLevel(logging.WARNING)


def main(**kwargs):
    div = '----------------------------------------------------------------------------------------'

    ini_file = kwargs.get("ini_file")
    yaml_path = kwargs.get("yaml_config_path")
    logger.info(div)
    logger.info('parsing yaml file')
    yaml = py.Yaml(yaml_path=yaml_path)

    if ini_file:
        sdk = looker_sdk.init40(config_file=ini_file)
    else:
        sdk = looker_sdk.init40()

    folder_metadata = yaml.get_folder_metadata()
    unnested_folder_metadata = fc.FolderConfig(
        folders=folder_metadata).unnest_folder_data()
    permission_set_metadata = yaml.get_permission_metadata()
    model_set_metadata = yaml.get_model_set_metadata()
    role_metadata = yaml.get_role_metadata()
    user_attribute_metadata = yaml.get_user_attribute_metadata()

################################################################
# Role Config ################################################
################################################################
    # Create Permission and Model Sets
    rc.CreateRoleBase(permissions=permission_set_metadata,
                      model_sets=model_set_metadata, sdk=sdk). execute()

################################################################
# Group Config ################################################
################################################################
    # CREATE NEW GROUPS FROM YAML FILE TEAM VALUES
    gc.CreateInstanceGroups(
        folders=unnested_folder_metadata, user_attributes=user_attribute_metadata, roles=role_metadata, sdk=sdk).execute()

    logger.info(div)

################################################################
# Role Config ################################################
################################################################
    up.CreateInstanceRoles(roles=role_metadata, sdk=sdk).execute()

    logger.info(div)

###############################################################
# Folder Config ################################################
###############################################################
    # CREATE NEW FOLDERS
    cf.CreateInstanceFolders(
        folder_metadata=unnested_folder_metadata, sdk=sdk).execute()
    cfp.CreateAndProvisionInstanceFolders(
        folders=unnested_folder_metadata, sdk=sdk).execute()

    logger.info(div)

###############################################################
# User Attribute Config #######################################
###############################################################
    # FIND UNIQUE USER ATTRIBUTES AND ATTRIBUTE TO TEAM
    cuap.CreateAndAssignUserAttributes(
        user_attributes=user_attribute_metadata, sdk=sdk).execute()

    logger.info('Lmanage has finished configuring your Looker instance!')


if __name__ == "__main__":
    instance = 'clustered'
    YP = ('/usr/local/google/home/hugoselbie/code_sample/py/'
          'lmanage/tests/example_yamls/clustered_output.yaml')
    IP = ('/usr/local/google/home/hugoselbie/code_sample/py/ini/dev.ini')

    main(
        ini_file=IP,
        yaml_config_path=YP)
