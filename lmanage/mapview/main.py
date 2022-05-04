'''
get dashboards
find elements on dashboards
get query elements of queries
get model files
get explores
get fields

get folder of lookml, or git repo
match dash field to lookml files
match how many times a lookml file has been referenced
show table definition of matched table
'''
from looker_sdk import init31
import logging
import coloredlogs
import instancedata as idata
import parse_lookml as pl
import mapexplores as me
import matched_field_analysis as mfa

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')
logging.getLogger("looker_sdk").setLevel(logging.WARNING)


def main(**kwargs):
    div = '-----------------------------------------------------------------------------'

    ini_file = kwargs.get("ini_file")
    lookml_file_path = kwargs.get("file_path")
    logger.info(div)
    sdk = init31(config_file=ini_file)

    dash_to_dash_elements = idata.get_dashboards(sdk=sdk)
    lookml_files = pl.get_all_lkml_filepaths(starting_path=lookml_file_path)

    parsed_lookml_dict = pl.get_parsed_lookml(lookml_file_paths=lookml_files)

    elements = me.match_element_to_lookml(
        instancedata=dash_to_dash_elements, view_file=lookml_files)
    da = mfa.MatchedFieldDataAnalysis(matched_fields=elements)
    print(da.most_used_object(looker_object='fields'))
    print(da.field_to_dashboard_map(dashboard_id_filter=7))
    da.data_analysis()


if __name__ == "__main__":
    IP = ('/usr/local/google/home/hugoselbie/code_sample/py/ini/k8.ini')
    FP = ('/usr/local/google/home/hugoselbie/code_sample/py/mapview/test_lookml_files/the_look')

    main(
        ini_file=IP,
        file_path=FP)
