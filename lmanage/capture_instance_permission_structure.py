import logging
import looker_sdk
import ruamel.yaml
from lmanage.capturator.user_group_capturation import role_config as rc
from lmanage.capturator.user_attribute_capturation import capture_ua_permissions as cup
from lmanage.capturator.folder_capturation import folder_config as fc, create_folder_yaml_structure as cfp
from lmanage.capturator.content_capturation import dashboard_capture as dc, look_capture as lc, board_capture as bc
from lmanage.utils import looker_object_constructors as loc, errorhandling as eh, logger_creation as log_color

def main(**kwargs):

    ini_file = kwargs.get("ini_file")
    yaml_path = kwargs.get("yaml_export_path")
    yaml_path = yaml_path.split('.')[0]
    logger_level = kwargs.get('verbose')
    logger = log_color.init_logger(__name__, logger_level)
    logger.info('creating yaml configuration file')

    if ini_file:
        sdk = looker_sdk.init40(config_file=ini_file)
    else:
        sdk = looker_sdk.init40()
    if eh.user_authentication_test(sdk=sdk):
        logger.info('User is successfully authenticated to the API')
    else:
        raise Exception(
            "User is not successfully authenticated please verify credentials")

    yaml = ruamel.yaml.YAML()
    yaml.register_class(loc.LookerFolder)
    yaml.register_class(loc.LookerModelSet)
    yaml.register_class(loc.LookerPermissionSet)
    yaml.register_class(loc.LookerRoles)
    yaml.register_class(loc.LookerUserAttribute)
    yaml.register_class(loc.LookObject)
    yaml.register_class(loc.DashboardObject)
    yaml.register_class(loc.BoardObject)
    yaml.register_class(looker_sdk.sdk.api40.models.ScheduledPlan)
    yaml.register_class(looker_sdk.sdk.api40.models.ScheduledPlanDestination)
    yaml.register_class(looker_sdk.sdk.api40.models.UserPublic)
###############################################################
# Capture Folder Config #######################################
###############################################################
    folder_returns = fc.CaptureFolderConfig(sdk=sdk, logger=logger).execute()
    folder_structure_list = folder_returns[1]

    with open(f'{yaml_path}.yaml', 'w') as file:
        fd_yml_txt = '''# FOLDER_PERMISSIONS\n# Opening Session Welcome to the Capturator, this is the Folder place\n# -----------------------------------------------------\n\n'''
        file.write(fd_yml_txt)
        yaml.dump(folder_structure_list, file)

    folder_root = folder_returns[0]

###############################################################
# Capture Roles ###############################################
###############################################################
    roles = rc.ExtractRoleInfo(sdk=sdk, logger=logger)

    looker_permission_sets = roles.extract_permission_sets()
    looker_model_sets = roles.extract_model_sets()

    looker_roles = roles.extract_role_info()
    with open(f'{yaml_path}.yaml', 'a') as file:
        r_yml_txt = '''# Looker Role\n# Opening Session Welcome to the Capturator, this is the Role place\n# -----------------------------------------------------\n\n'''
        file.write(r_yml_txt)

        file.write('\n\n# PERMISSION SETS\n')
        yaml.dump(looker_permission_sets, file)
        file.write('\n\n# MODEL SETS\n')
        yaml.dump(looker_model_sets, file)
        file.write('\n\n# LOOKER ROLES\n')
        yaml.dump(looker_roles, file)
###############################################################
# Capture User Attributes #####################################
###############################################################
    looker_ua = cup.ExtractUserAttributes(sdk=sdk, logger=logger).create_user_attributes()
    with open(f'{yaml_path}.yaml', 'a') as file:
        file.write('\n\n# USER_ATTRIBUTES\n')
        yaml.dump(looker_ua, file)

###############################################################
# Capture Users Content #######################################
###############################################################
    # Capture Content Boards
    # boards = bc.CaptureBoards(sdk=sdk).execute()
    # with open(f'{yaml_path}_content.yaml', 'w+') as file:
    #     file.write('\n\n# BoardData\n')
    #     yaml.dump(boards, file)

    lcapture = lc.LookCapture(
        sdk=sdk, folder_root=folder_root, logger=logger)
    looks = lcapture.execute()

    with open(f'{yaml_path}_content.yaml', 'wb') as file:
        file.write(bytes('\n\n# LookData\n', 'utf-8'))

        if eh.test_object_data(looks):
            looks = looks
            yaml.dump(looks, file)
        else:
            looks = bytes('#No Captured Looks', 'utf-8')
            file.write(looks)

    # Capture Dashboard Content
    dash_content = dc.CaptureDashboards(
        sdk=sdk, folder_root=folder_root, logger=logger).execute()
    with open(f'{yaml_path}_content.yaml', 'ab') as file:
        fd_yml_txt = bytes('\n\n# Dashboard Content\n', 'utf-8')
        file.write(fd_yml_txt)
        if eh.test_object_data(dash_content):
            dash_content = dash_content
            yaml.dump(dash_content, file)
        else:
            dash_content = bytes('#No Captured Dashboards', 'utf-8')
            file.write(dash_content)

        
    # FIND UNIQUE USER ATTRIBUTES AND ATTRIBUTE TO TEAM
    logger.info('\n\n\n Lmanage has finished capturing your Looker instance!\n')
    logger.info('\n\nplease find captured settings metadata at: \n%s.yaml \n\ncaptured content metadata at:\n%s_content.yaml', yaml_path, yaml_path)


if __name__ == "__main__":
    instance = 'dev'
    IP = (
        f'/usr/local/google/home/hugoselbie/code_sample/py/ini/{instance}.ini')
    YP = (
        f'/usr/local/google/home/hugoselbie/code_sample/py/lmanage/tests/example_yamls/{instance}_output.yaml')

    main(yaml_export_path=YP, ini_file=IP)
