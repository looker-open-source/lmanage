import os
import lkml
import glob
import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')
logging.getLogger("looker_sdk").setLevel(logging.WARNING)


def get_all_lkml_filepaths(starting_path):
    logger.info(starting_path)
    lookml_files = [f for f in glob.glob(
        starting_path + "/**/*" + 'lkml', recursive=True)]
    logger.debug(lookml_files)
    return lookml_files


def parse_lookml(path):
    with open(path, 'r') as lookml_file:
        lookml = lkml.load(lookml_file)
        return lookml


def get_parsed_lookml(lookml_file_paths):
    response = []
    for file in lookml_file_paths:
        parsed_lookml = parse_lookml(file)
        logger.debug(parsed_lookml)
        temp = {}
        temp[file] = parsed_lookml
        response.append(temp)
    return response


'''
    parse a LookML file from lmanage.LookML to JSON
    Authors:
            Carl Anderson (carl.anderson@weightwatchers.com)
'''


class LookML():

    def __init__(self, infilepath):
        '''parse the LookML infilepath, convert to JSON, and then read into JSON object
        Args:
            infilepath (str): path to input LookML file
        Returns:
            JSON object of LookML
        '''
        if not os.path.exists(infilepath):
            raise IOError("Filename does not exist: %s" % infilepath)

        self.infilepath = infilepath
        if infilepath.endswith(".model.lkml"):
            self.filetype = 'model'
        elif infilepath.endswith(".view.lkml"):
            self.filetype = 'view'
        elif infilepath.endswith(".explore.lkml"):
            self.filetype = 'explore'
        elif infilepath.endswith(".lkml"):
            self.filetype = 'generic'

        else:
            raise Exception("Unsupported filename " + infilepath)
        self.base_filename = os.path.basename(infilepath)
        self.base_name = self.base_filename.replace(".model.lkml", "").replace(
            ".explore.lkml", "").replace(".view.lkml", "")

        with open(infilepath, 'r') as file:
            self.json_data = lkml.load(file)

    def views(self):
        """get views (if any) from lmanage.the LookML
        Returns:
            views (list) if any, None otherwise
        """
        if 'views' in self.json_data:
            return self.json_data['views']
        return None

    def has_views(self):
        """does this have one or more views?
        Returns:
            bool, whether this has views
        """
        vs = self.views()
        return (vs and len(vs) > 0)

    def explores(self):
        """get explores (if any) from lmanage.the LookML
        Returns:
            explores (list) if any, None otherwise
        """
        if 'explores' in self.json_data:
            return self.json_data['explores']
        return None

    def has_explores(self):
        """does this have one or more explores?
        Returns:
            bool, whether this has explores
        """
        es = self.explores()
        return (es and len(es) > 0)
