import looker_sdk
from lmanage.logger_config import setup_logger
from looker_sdk import error

logger = setup_logger()


class LookerAuth():
    def authenticate(self, ini_file):
        sdk = looker_sdk.init40(
            config_file=ini_file) if ini_file else looker_sdk.init40()
        if self.__auth_check(sdk):
            logger.info('User is successfully authenticated to the API')
            return sdk
        else:
            raise Exception(
                'User is not successfully authenticated.  Please verify credentials in .ini file.')

    def __auth_check(self, sdk):
        try:
            sdk.me()
            return True
        except error.SDKError():
            return False
