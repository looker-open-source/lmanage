from lmanage.looker_auth import LookerAuth
from lmanage.configurator.user_attribute_configuration import create_and_assign_user_attributes as cuap
from lmanage.configurator.folder_configuration import create_and_provision_instance_folders as cfp, create_instance_folders as cf
from lmanage.configurator.user_group_configuration import create_instance_groups as gc, create_instance_roles as up, create_role_base as rc
from lmanage.configurator.content_configuration import clean_instance_content as ccp, create_looks as cl, create_dashboards as cd, create_boards as cb
from lmanage.utils import logger_creation as log_color


class LookerProvisioner():
    def __init__(self, ini_file):
        self.sdk = LookerAuth().authenticate(ini_file)
        logger_level = 'INFO'  # kwargs.get('verbose')
        self.logger = log_color.init_logger(__name__, logger_level)
        self.logger.info(
            '----------------------------------------------------------------------------------------')
        self.logger.info('provisioning')

    def provision(self, metadata):
        ###############
        # Role Config #
        ###############
        # Create Permission and Model Sets
        rc.CreateRoleBase(permissions=metadata['permission_set_metadata'],
                          model_sets=metadata['model_set_metadata'], sdk=self.sdk, logger=self.logger).execute()

        #################
        # Folder Config #
        #################
        # CREATE NEW FOLDERS
        folder_objects = cf.CreateInstanceFolders(
            folder_metadata=metadata['folder_metadata'], sdk=self.sdk, logger=self.logger)
        created_folder_metadata = folder_objects.create_folders()

        # CREATE FOLDER TO FOLDER Dict
        folder_mapping_obj = folder_objects.create_folder_mapping_dict(
            folder_metadata=created_folder_metadata)

        ################
        # Group Config #
        ################
        # CREATE NEW GROUPS FROM YAML FILE TEAM VALUES
        gc.CreateInstanceGroups(
            folders=created_folder_metadata,
            user_attributes=metadata['user_attribute_metadata'],
            roles=metadata['role_metadata'],
            sdk=self.sdk,
            logger=self.logger).execute()

        ###########################
        # Folder Provision Config #
        ###########################
        # CREATE NEW GROUPS FROM YAML FILE TEAM VALUES
        cfp.CreateAndProvisionInstanceFolders(
            folders=created_folder_metadata,
            sdk=self.sdk, logger=self.logger).execute()

        # ###############
        # # Role Config #
        # ###############
        up.CreateInstanceRoles(roles=metadata['role_metadata'],
                               sdk=self.sdk,
                               logger=self.logger).execute()

        # #########################
        # # User Attribute Config #
        # #########################
        # FIND UNIQUE USER ATTRIBUTES AND ATTRIBUTE TO TEAM
        cuap.CreateAndAssignUserAttributes(
            user_attributes=metadata['user_attribute_metadata'],
            sdk=self.sdk,
            logger=self.logger).execute()

        ############################
        # Content Transport Config #
        ############################
        # EMPTY TRASH CAN OF ALL DELETED CONTENT
        ccp.CleanInstanceContent(sdk=self.sdk, logger=self.logger).execute()

        # FIND LOOKS AND REMAKE THEM
        cl.CreateLooks(
            sdk=self.sdk,
            folder_mapping=folder_mapping_obj,
            content_metadata=metadata['look_metadata'],
            logger=self.logger).execute()

        # Find DASHBOARDS AND REMAKE THEM
        cd.CreateDashboards(
            sdk=self.sdk,
            folder_mapping=folder_mapping_obj,
            content_metadata=metadata['dashboard_metadata'],
            logger=self.logger).execute()
