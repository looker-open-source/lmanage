from attr import field
import lkml
import glob
import logging
import coloredlogs
import ast
import pandas as pd

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
