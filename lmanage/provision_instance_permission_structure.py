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
from lmanage.configurator.content_configuration import create_looks as cl
from lmanage.configurator.content_configuration import create_dashboards as cd
from lmanage.configurator.content_configuration import create_content_prep as ccp
from lmanage.utils import parse_yaml as py


logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')
logging.getLogger("looker_sdk").setLevel(logging.WARNING)


def main(**kwargs):
    div = '----------------------------------------------------------------------------------------'

    ini_file = kwargs.get("ini_file")
    yaml_path = kwargs.get("yaml_config_path")
    logger.info(div)
    #logger.info('parsing yaml file')
    yaml_split = yaml_path.split('.')
    settings_yaml = py.Yaml(yaml_path=f'{yaml_split[0]}.yaml')
    content_yaml = py.Yaml(yaml_path=f'{yaml_split[0]}_content.yaml')

    if ini_file:
        sdk = looker_sdk.init40(config_file=ini_file)
    else:
        sdk = looker_sdk.init40()

    folder_metadata = settings_yaml.get_folder_metadata()
    if not folder_metadata:
        logger.warn(
            f'no folder_metadata specified please check your yaml file at {yaml_split[0]}.yaml')
    permission_set_metadata = settings_yaml.get_permission_metadata()
    if not permission_set_metadata:
        logger.warn(
            f'no permission_set_metadata specified please check your yaml file at {yaml_split[0]}.yaml')
    model_set_metadata = settings_yaml.get_model_set_metadata()
    if not model_set_metadata:
        logger.warn(
            f'no model_set_metadata specified please check your yaml file at {yaml_split[0]}.yaml')
    role_metadata = settings_yaml.get_role_metadata()
    if not role_metadata:
        logger.warn(
            f'no role_metadata specified please check your yaml file at {yaml_split[0]}.yaml')
    user_attribute_metadata = settings_yaml.get_user_attribute_metadata()
    if not user_attribute_metadata:
        logger.warn(
            f'no user_attribute_metadata specified please check your yaml file at {yaml_split[0]}.yaml')

    look_metadata = content_yaml.get_look_metadata()
    if not look_metadata:
        logger.warn(
            f'no look_metadata specified please check your yaml file at {yaml_split[0]}_content.yaml')

    dash_metadata = content_yaml.get_dash_metadata()
    if not dash_metadata:
        logger.warn(
            f'no dash_metadata specified please check your yaml file at {yaml_split[0]}_content.yaml')


################################################################
# Role Config ################################################
################################################################
    # Create Permission and Model Sets
    rc.CreateRoleBase(permissions=permission_set_metadata,
                      model_sets=model_set_metadata, sdk=sdk).execute()

# ###############################################################
# Folder Config ################################################
###############################################################
    # CREATE NEW FOLDERS
    folder_objects = cf.CreateInstanceFolders(
        folder_metadata=folder_metadata, sdk=sdk)
    created_folder_metadata = folder_objects.create_folders()

    # CREATE FOLDER TO FOLDER Dict
    folder_mapping_obj = folder_objects.create_folder_mapping_dict(
        folder_metadata=created_folder_metadata)


################################################################
# Group Config ################################################
################################################################
    # CREATE NEW GROUPS FROM YAML FILE TEAM VALUES
    gc.CreateInstanceGroups(
        folders=created_folder_metadata, user_attributes=user_attribute_metadata, roles=role_metadata, sdk=sdk).execute()

################################################################
# Folder Provision Config ################################################
################################################################
    # CREATE NEW GROUPS FROM YAML FILE TEAM VALUES

    cfp.CreateAndProvisionInstanceFolders(
        folders=created_folder_metadata, sdk=sdk).execute()

################################################################
# Role Config ################################################
################################################################
    up.CreateInstanceRoles(roles=role_metadata, sdk=sdk).execute()

###############################################################
# User Attribute Config #######################################
###############################################################
    # FIND UNIQUE USER ATTRIBUTES AND ATTRIBUTE TO TEAM
    cuap.CreateAndAssignUserAttributes(
        user_attributes=user_attribute_metadata, sdk=sdk).execute()

###############################################################
# Content Transport Config #######################################
###############################################################
    # EMPTY TRASH CAN OF ALL DELETED CONTENT
    ccp.CleanInstanceContent(sdk=sdk).execute()
    
    # FIND LOOKS AND REMAKE THEM
    look_creator = cl.CreateInstanceLooks(
        folder_mapping=folder_mapping_obj, sdk=sdk, content_metadata=look_metadata)
    look_creator.execute()

    # Find DASHBOARDS AND REMAKE THEM
    dash_creator = cd.Create_Dashboards(
        sdk=sdk, folder_mapping=folder_mapping_obj, content_metadata=dash_metadata)
    dash_creator.execute()

    logger.info('lmanage has finished configuring your Looker instance!')


if __name__ == "__main__":
    YP = ('/usr/local/google/home/hugoselbie/code_sample/py/'
          'lmanage/tests/example_yamls/dev_output.yaml')
    IP = ('/usr/local/google/home/hugoselbie/code_sample/py/ini/dev.ini')

    main(
        ini_file=IP,
        yaml_config_path=YP)
