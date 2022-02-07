import logging
import coloredlogs
import looker_sdk
from .create_folder_permissions import create_folder_permissions as cfp
from .create_user_permissions import user_permission as up
from .create_user_attribute_permissions import create_ua_permissions as cuap
from .utils import group_config as gc
from .utils import folder_config as fc
from .utils import parse_yaml as py


logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')


def main(**kwargs):
    div = '--------------------------------------'

    ini_file = kwargs.get("ini_file")
    yaml_path = kwargs.get("yaml_config_path")
    logger.info(div)
    logger.info('parsing yaml file')
    yaml = py.Yaml(yaml_path=yaml_path)
    instance_config = yaml.read_provision_yaml()
    if ini_file:
        sdk = looker_sdk.init31(config_file=ini_file)
    else:
        sdk = looker_sdk.init31()

###############################################################
# Group Config ################################################
###############################################################
    # # FIND UNIQUE GROUPS FROM YAML FILE
    unique_group_names = gc.get_unique_groups(parsed_yaml=instance_config)
    logger.info(div)

    # # CREATE NEW GROUPS
    group_metadata = gc.get_group_metadata(
        sdk=sdk, unique_group_list=unique_group_names)
    logger.info(div)

    # # DELETE ALL GROUPS THAT DO NOT MATCH WITH YAML
    gc.sync_groups(group_name_list=unique_group_names,
                   group_metadata_list=group_metadata, sdk=sdk)
    logger.info(div)

###############################################################
# Role Config ################################################
###############################################################
    # # FIND UNIQUE ROLES
    role_metadata = up.get_role_metadata(parsed_yaml=instance_config)

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
    created_role_metadata = up.create_roles(sdk=sdk,
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
    # # FIND UNIQUE FOLDERS
    unique_folder_names = fc.get_unique_folders(
        sdk=sdk, parsed_yaml=instance_config)
    logger.info(div)

    # # CREATE NEW FOLDERS
    folder_metadata = fc.get_folder_metadata(
        sdk=sdk, unique_folder_list=unique_folder_names)
    logger.info(div)

    # # CONFIGURE FOLDERS WITH EDIT AND VIEW ACCESS
    content_access_metadata = cfp.get_content_access_metadata(
        sdk=sdk,
        parsed_yaml=instance_config)

    # # ADD AND SYNC CONTENT VIEW ACCESS WITH YAML
    cfp.provision_folders_with_group_access(
        sdk=sdk, content_access_metadata_list=content_access_metadata)

    cfp.remove_all_user_group(
        sdk=sdk, content_access_metadata_list=content_access_metadata)
    # # DELETE ALL FOLDERS THAT DON'T MATCH WITH YAML
    fc.sync_folders(sdk=sdk, folder_metadata_list=folder_metadata,
                    folder_name_list=unique_folder_names)

    logger.info(div)

################################################################
## User Attribute Config #######################################
################################################################
#    # # FIND UNIQUE USER ATTRIBUTES
#    ua_metadata = cuap.get_user_attribute_metadata(
#        sdk=sdk,
#        parsed_yaml=instance_config)

#    # # CREATE NEW FOLDERS

#    cuap.create_user_attribute(
#        sdk=sdk,
#        ua_metadata=ua_metadata
#    )

#    # # CONFIGURE FOLDERS WITH EDIT AND VIEW ACCESS

#    # # ADD AND SYNC CONTENT VIEW ACCESS WITH YAML

#    # # DELETE ALL FOLDERS THAT DON'T MATCH WITH YAML


if __name__ == "__main__":
    YP = ('/usr/local/google/home/hugoselbie/code_sample/py/'
          'lmanage/tests/example_yamls/fullinstance.yaml')
    IP = ('/usr/local/google/home/hugoselbie/code_sample/py/ini/k8.ini')

    main(
        ini_file=IP,
        yaml_config_path=YP)
    logger.info('I have finished')
