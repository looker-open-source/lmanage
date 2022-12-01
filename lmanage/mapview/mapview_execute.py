from looker_sdk import init31
import logging
import coloredlogs
import mapview.instancedata as idata
import mapview.parse_sql_tables as pst
import mapview.compare_content_to_lookml as me
import mapview.matched_field_analysis as mfa
from lmanage.mapview.utils import parse_lookml as pl

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')
logging.getLogger("looker_sdk").setLevel(logging.WARNING)


def main(**kwargs):
    div = '-------------------------------------------------------------------'

    ini_file = kwargs.get("ini_file")
    lookml_file_path = kwargs.get("lookml_file_path")
    file_output = kwargs.get("output_path")
    logger.info(div)
    sdk = init31(config_file=ini_file)

    dashboard_metadata = idata.GetCleanInstanceData(sdk=sdk).execute()

    query_elements = pst.ParseSqlTables(dataextract=dashboard_metadata,
                                        sdk=sdk).get_sql_from_elements()

    lookml_files = pl.get_all_lkml_filepaths(starting_path=lookml_file_path)

    elements = me.match_element_to_lookml(
        instancedata=query_elements, view_file=lookml_files)
    da = mfa.MatchedFieldDataAnalysis(matched_fields=elements)

    da.export_to_excel(file_output)
    logger.info('i have finished')


if __name__ == "__main__":
    IP = ('/usr/local/google/home/hugoselbie/code_sample/py/ini/k8.ini')
    FP = ('/usr/local/google/home/hugoselbie/code_sample/py/mapview/test_lookml_files/the_look')

    main(
        ini_file=IP,
        file_path=FP)
