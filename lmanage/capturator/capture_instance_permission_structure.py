import logging
import coloredlogs
import looker_sdk
from user_group_configuration import group_config as gc

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')
logging.getLogger("looker_sdk").setLevel(logging.WARNING)


def main(**kwargs):
    div = '-------------------------------------------------------------------'

    ini_file = kwargs.get("ini_file")
    logger.info(div)
    logger.info('parsing yaml file')

    if ini_file:
        sdk = looker_sdk.init31(config_file=ini_file)
    else:
        sdk = looker_sdk.init31()


##############################################################
# Folder Config ################################################
###############################################################
    # CREATE NEW FOLDERS
    x = gc.GetInstanceGroups(sdk=sdk).extract_folder_names()
    print(x)

    logger.info(div)

###############################################################
# User Attribute Config #######################################
###############################################################
    # FIND UNIQUE USER ATTRIBUTES AND ATTRIBUTE TO TEAM
    # cuap.CreateAndAssignUserAttributes(
    #     user_attributes=user_attribute_metadata, sdk=sdk).execute()

    # logger.info('Lmanage has finished configuring your Looker instance!')


if __name__ == "__main__":
    IP = ('/usr/local/google/home/hugoselbie/code_sample/py/ini/k8.ini')

    main(ini_file=IP)
