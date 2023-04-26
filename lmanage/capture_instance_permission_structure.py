import logging
import coloredlogs
import looker_sdk
import ruamel.yaml
import json
from lmanage.capturator.user_group_capturation import role_config as rc
from lmanage.capturator.user_attribute_capturation import capture_ua_permissions as cup
from lmanage.capturator.folder_capturation import folder_config as fc
from lmanage.capturator.folder_capturation import create_folder_yaml_structure as cfp
from lmanage.capturator.content_capturation import dashboard_capture as dc
from lmanage.capturator.content_capturation import look_capture as lc
from lmanage.utils import looker_object_constructors as loc

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')
logging.getLogger("looker_sdk").setLevel(logging.WARNING)


def main(**kwargs):

    ini_file = kwargs.get("ini_file")
    yaml_path = kwargs.get("yaml_export_path")
    yaml_path = yaml_path.split('.')[0]

    logger.info('creating yaml configuration file')

    if ini_file:
        sdk = looker_sdk.init40(config_file=ini_file)
    else:
        sdk = looker_sdk.init40()

    yaml = ruamel.yaml.YAML()
    yaml.register_class(loc.LookerFolder)
    yaml.register_class(loc.LookerModelSet)
    yaml.register_class(loc.LookerPermissionSet)
    yaml.register_class(loc.LookerRoles)
    yaml.register_class(loc.LookerUserAttribute)
    yaml.register_class(loc.LookObject)
    yaml.register_class(loc.DashboardObject)

###############################################################
# Capture Folder Config #######################################
###############################################################
    folder_returns = fc.CaptureFolderConfig(sdk=sdk).execute()
    folder_structure_list = folder_returns[1]

    with open(f'{yaml_path}.yaml', 'w') as file:
        fd_yml_txt = '''# FOLDER_PERMISSIONS\n# Opening Session Welcome to the Capturator, this is the Folder place\n# -----------------------------------------------------\n\n'''
        file.write(fd_yml_txt)
        yaml.dump(folder_structure_list, file)

    folder_root_dict = folder_returns[0]

###############################################################
# Capture Roles ###############################################
###############################################################
    roles = rc.ExtractRoleInfo(sdk=sdk)

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
    looker_ua = cup.ExtractUserAttributes(sdk=sdk).create_user_attributes()
    yaml.register_class(cup.LookerUserAttribute)
    with open(f'{yaml_path}.yaml', 'a') as file:
        file.write('\n\n# USER_ATTRIBUTES\n')
        yaml.dump(looker_ua, file)

###############################################################
# Capture Users Content #######################################
###############################################################
    # Capture Look Content
    looks = lc.CaptureLookObject(sdk=sdk, folder_root=folder_root_dict).execute()
    with open(f'{yaml_path}_content.yaml', 'w+') as file:
        file.write('\n\n# LookData\n')
        yaml.dump(looks, file)

    # Capture Dashboard Content
    dash_content = dc.CaptureDashboards(sdk=sdk, folder_root=folder_root_dict).execute()
    with open(f'{yaml_path}_content.yaml', 'a') as file:
        fd_yml_txt = '\n\n# Dashboard Content\n'
        file.write(fd_yml_txt)
        yaml.dump(dash_content, file)


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
