import logging
import coloredlogs
import looker_sdk
from folder_configuration import create_folder_permissions as cfp, folder_config as fc
from lmanage.configurator import user_attribute_configuration
from user_group_configuration import user_permission as up, group_config as gc, role_config as rc
from user_attribute_configuration import create_ua_permissions as cuap
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
    permission_set_metadata = yaml.get_permission_metadata()
    model_set_metadata = yaml.get_model_set_metadata()
    role_metadata = yaml.get_role_metadata()
    user_attribute_metadata = yaml.get_user_attribute_metadata()

################################################################
# Role Config ################################################
################################################################
    # Create Permission and Model Sets
    role_base = rc.CreateRoleBase(permissions=permission_set_metadata,
                                  model_sets=model_set_metadata, sdk=sdk)
    role_base.create_role_building_blocks()

################################################################
# Group Config ################################################
################################################################
    # FIND UNIQUE GROUPS FROM YAML FILE
    yaml_folder_metadata = fc.get_folder_metadata(
        folder_metadata=yaml.get_folder_metadata())
    logger.info(div)

    unique_group_names = gc.get_unique_groups(
        parsed_yaml=yaml.get_role_metadata(), yaml_folders=yaml_folder_metadata)
    logger.info(div)
    sdk.lj

    # CREATE NEW GROUPS
    group_metadata = gc.get_group_metadata(
        sdk=sdk, unique_group_list=unique_group_names)
    logger.info(div)

    # DELETE ALL GROUPS THAT DO NOT MATCH WITH YAML
    gc.sync_groups(group_name_list=unique_group_names,
                   group_metadata_list=group_metadata, sdk=sdk)
    logger.info(div)

################################################################
## Role Config ################################################
################################################################
    # # FIND UNIQUE ROLES
    role_metadata = up.get_role_metadata(parsed_yaml=yaml.get_role_metadata())

    # # CREATE PERMISSION SETS
    permission_set_metadata = up.create_permission_set(
        sdk=sdk, permission_set_list=role_metadata)

    # # SYNC PERMISSION SETS
    all_permission_sets = sdk.all_permission_sets()
    up.sync_permission_set(
        sdk=sdk, all_permission_sets=all_permission_sets,
        permission_set_list=permission_set_metadata)

    # # CREATE MODEL SETS
    model_set_metadata = up.create_model_set(
        sdk=sdk, model_set_list=role_metadata)

    # # SYNC MODEL SETS
    all_model_sets = sdk.all_model_sets()
    up.sync_model_set(sdk=sdk,
                      all_model_sets=all_model_sets,
                      model_set_list=model_set_metadata)

    # # CREATE NEW ROLES
    created_role_metadata = up.create_roles(
        sdk=sdk,
        all_model_sets=all_model_sets,
        all_permission_sets=all_permission_sets,
        role_metadata_list=role_metadata)

    # # SYNC ROLES
    all_roles = sdk.all_roles()
    up.sync_roles(
        sdk=sdk,
        all_roles=all_roles,
        role_metadata_list=created_role_metadata
    )
    # # ATTACH ROLES TO TEAM GROUPS
    up.attach_role_to_group(sdk=sdk,
                            role_metadata=role_metadata,
                            created_role_metadata=created_role_metadata,
                            all_roles=all_roles)

###############################################################
# Folder Config ################################################
###############################################################
    # CREATE NEW FOLDERS
    instance_folder_metadata = fc.create_looker_folder_metadata(
        sdk=sdk, unique_folder_list=yaml_folder_metadata)
    logger.info(div)

    # CONFIGURE FOLDERS WITH EDIT AND VIEW ACCESS
    content_access_metadata = cfp.get_content_access_metadata(
        sdk=sdk,
        instance_folder_metadata=instance_folder_metadata)

    # # ADD AND SYNC CONTENT VIEW ACCESS WITH YAML
    cfp.provision_folders_with_group_access(
        sdk=sdk, content_access_metadata_list=content_access_metadata)

    cfp.remove_all_user_group(
        sdk=sdk, content_access_metadata_list=content_access_metadata)
    # # DELETE ALL FOLDERS THAT DON'T MATCH WITH YAML
    fc.sync_folders(sdk=sdk, folder_metadata_list=instance_folder_metadata)

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
