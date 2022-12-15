import logging
import coloredlogs
import looker_sdk
import ruamel.yaml
from lmanage.capturator.user_group_capturation import role_config as rc
from lmanage.capturator.user_attribute_capturation import capture_ua_permissions as cup
from lmanage.capturator.folder_capturation import folder_config as fc
from lmanage.capturator.folder_capturation import create_folder_yaml_structure as cfp
from lmanage.utils import looker_object_constructors as loc

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')
logging.getLogger("looker_sdk").setLevel(logging.WARNING)


def main(**kwargs):
    div = '-------------------------------------------------------------------'

    ini_file = kwargs.get("ini_file")
    yaml_path = kwargs.get("yaml_export_path")
    logger.info(div)
    logger.info('creating yaml configuration file')

    if ini_file:
        sdk = looker_sdk.init40(config_file=ini_file)
    else:
        sdk = looker_sdk.init40()

    yaml = ruamel.yaml.YAML()

###############################################################
# Capture Folder Config #######################################
###############################################################
    folder_structurelist = fc.CaptureFolderConfig(sdk=sdk).execute()
    yaml.register_class(loc.LookerFolder)
    print(f'{yaml_path}')
    with open(f'{yaml_path}', 'w') as file:
        fd_yml_txt = '''# FOLDER_PERMISSIONS\n# Opening Session Welcome to the Capturator, this is the Folder place\n# -----------------------------------------------------\n\n'''
        file.write(fd_yml_txt)
        # file.write('# FOLDER_PERMISSIONS\n')
        yaml.dump(folder_structurelist, file)

    # yaml.dump(folder_structurelist, sys.stdout)

    logger.info(div)
###############################################################
# Capture Roles ###############################################
###############################################################
    roles = rc.ExtractRoleInfo(sdk=sdk)

    looker_permission_sets = roles.extract_permission_sets()
    looker_model_sets = roles.extract_model_sets()

    looker_roles = roles.extract_role_info()
    yaml.register_class(rc.LookerModelSet)
    yaml.register_class(rc.LookerPermissionSet)
    yaml.register_class(rc.LookerRoles)
    with open(f'{yaml_path}', 'a') as file:
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
    with open(f'{yaml_path}', 'a') as file:
        file.write('\n\n# USER_ATTRIBUTES\n')
        yaml.dump(looker_ua, file)

    # FIND UNIQUE USER ATTRIBUTES AND ATTRIBUTE TO TEAM
    logger.info('Lmanage has finished capturing your Looker instance!')
    logger.info('please find the captured instance at %s', yaml_path)


if __name__ == "__main__":
    instance = 'demo'
    IP = (
        f'/usr/local/google/home/hugoselbie/code_sample/py/ini/{instance}.ini')
    YP = (
        f'/usr/local/google/home/hugoselbie/code_sample/py/lmanage/tests/example_yamls/{instance}_output.yaml')

    main(yaml_export_path=YP, ini_file=IP)
