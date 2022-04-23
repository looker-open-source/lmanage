import logging
import coloredlogs
import looker_sdk
from user_attribute_configuration import create_ua_permissions as cuap
from folder_configuration import folder_config as fc
from folder_configuration import create_folder_permissions as cfp
from user_group_configuration import role_config as rc
from user_group_configuration import group_config as gc
from user_group_configuration import user_permission as up
from utils import parse_yaml as py


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
        sdk = looker_sdk.init31(config_file=ini_file)
    else:
        sdk = looker_sdk.init31()

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
    cfp.CreateAndProvisionInstanceFolders(
        folders=folder_metadata, sdk=sdk).execute()
    # fc.FolderConfig.execute()
    # instance_folder_metadata = fc.create_looker_folder_metadata(
    #     sdk=sdk, unique_folder_list=yaml_folder_metadata)
    # logger.info(div)

    # # CONFIGURE FOLDERS WITH EDIT AND VIEW ACCESS
    # content_access_metadata = cfp.get_content_access_metadata(
    #     sdk=sdk,
    #     instance_folder_metadata=instance_folder_metadata)

    # # # ADD AND SYNC CONTENT VIEW ACCESS WITH YAML
    # cfp.provision_folders_with_group_access(
    #     sdk=sdk, content_access_metadata_list=content_access_metadata)

    # cfp.remove_all_user_group(
    #     sdk=sdk, content_access_metadata_list=content_access_metadata)
    # # # DELETE ALL FOLDERS THAT DON'T MATCH WITH YAML
    # fc.sync_folders(sdk=sdk, folder_metadata_list=instance_folder_metadata)

    logger.info(div)

###############################################################
# User Attribute Config #######################################
###############################################################
    # FIND UNIQUE USER ATTRIBUTES
    ua_metadata = cuap.get_user_attribute_metadata(
        sdk=sdk,
        parsed_yaml=instance_config)

    # CREATE NEW USER ATTRIBUTES
    cuap.create_user_attribute_if_not_exists(
        sdk=sdk,
        ua_metadata=ua_metadata
    )

    # DELETE ALL USER ATTRIBUTES THAT DON'T MATCH WITH YAML
    cuap.sync_user_attributes(
        sdk=sdk,
        ua_metadata=ua_metadata
    )

    # ADD VALUES TO INSCOPE USER ATTRIBUTES
    cuap.add_group_values_to_ua(
        sdk=sdk,
        ua_metadata=ua_metadata
    )

    logger.info('Lmanage has finished configuring your Looker instance!')


if __name__ == "__main__":
    YP = ('/usr/local/google/home/hugoselbie/code_sample/py/'
          'lmanage/tests/example_yamls/fullinstance.yaml')
    IP = ('/usr/local/google/home/hugoselbie/code_sample/py/ini/k8.ini')

    main(
        ini_file=IP,
        yaml_config_path=YP)
