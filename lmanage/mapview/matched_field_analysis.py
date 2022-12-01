from lmanage.attr import field
import lkml
import glob
import logging
import coloredlogs
import ast
import pandas as pd
import xlsxwriter

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')
logging.getLogger("looker_sdk").setLevel(logging.WARNING)


class MatchedFieldDataAnalysis():
    def __init__(self, matched_fields):
        self.matched_data = matched_fields
        self.df = pd.DataFrame(self.matched_data)

    def create_df(self):
        df = pd.DataFrame(self.matched_data)
        return df

    def most_used_object(self, looker_object):
        if looker_object == 'views':
            xploded = self.df.explode('used_views')
            xploded = xploded.groupby(['used_views'])['dashboard'].count()
            return xploded
        elif looker_object == 'fields':
            xploded = self.df.explode('matched_fields')
            xploded = xploded.groupby(['matched_fields'])['dashboard'].count()
            xploded = xploded.groupby(['used_views'])[
                'dashboard'].count().rename('dashboard_count').sort_values(ascending=False)
            return xploded

    def field_to_dashboard_map(self, field_filter=None, dashboard_id_filter=None):
        xploded = self.df.explode('matched_fields')
        if field_filter:
            xploded = xploded.filter(like=field_filter, axis=0)
        if dashboard_id_filter:
            xploded = xploded.filter(like=dashboard_id_filter)
        return xploded

    def data_analysis(self):
        df = self.create_df()
        print(df)

    def export_to_excel(self, output):
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        dashboard_match = self.field_to_dashboard_map()
        used_views = self.most_used_object(looker_object='views')
        used_obj = self.most_used_object(looker_object='fields')

        # Write each dataframe to a different worksheet.
        dashboard_match.to_excel(writer, sheet_name='DashboardToLookMLMapping')
        used_obj.to_excel(writer, sheet_name='MostUsedDimensions')
        used_views.to_excel(writer, sheet_name='MostUsedViews')

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()
