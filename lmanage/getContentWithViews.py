import looker_sdk
import configparser as ConfigParser
from icecream import ic
import pandas as pd

# -----------------------------------------------------------
# Looker API Script to Identify Used Views for each piece of Looker content
# Tested on UDD's and Looks only
# email hugoselbie@google.com
# -----------------------------------------------------------


def get_content_id_title(sdk):
    '''
    Function captures all metadata for dashboard's and looks and outputs a list of content id, content type, title
    '''
    content_metadata = []
    dashboard_content = sdk.all_dashboards()
    look_content = sdk.all_looks()

    for dashboards in range(0, len(dashboard_content)):
        response = {}
        response['content_type'] = 'dashboard'
        response['dashboard_title'] = dashboard_content[dashboards].title
        response['dashboard_id'] = dashboard_content[dashboards].id
        content_metadata.append(response)

    for looks in range(0, len(look_content)):
        response = {}
        response['content_type'] = 'look'
        response['look_title'] = look_content[looks].title
        response['look_id'] = look_content[looks].id
        content_metadata.append(response)

    return content_metadata


def find_content_views(looker_content: list, sdk):
    '''
    Function loops through inputted list and isolates used fields and filters in specific content
    and exports as a list of dictionaries for easy pandas input. Filter fields are parsed and added to 
    field output.
    '''
    element_info = []
    for content in looker_content:
        if content.get('content_type') == 'dashboard':
            db_metadata = sdk.dashboard_dashboard_elements(
                dashboard_id=content.get('dashboard_id'))

            for element in range(0, len(db_metadata)):
                response = {}
                response['content_type'] = content.get('content_type')
                response['dashboard_title'] = content.get('dashboard_title')
                response['element_id'] = db_metadata[element].id
                response['dashboard_id'] = db_metadata[element].dashboard_id
                fields = db_metadata[element].query.fields
                try:
                    filters = db_metadata[element].query.filters.keys()
                    for filter in list(filters):
                        fields.append(filter)
                    response['fields'] = fields
                except AttributeError as no_filter:
                    response['fields'] = fields

                element_info.append(response)

        elif content.get('content_type') == 'look':
            look_metadata = sdk.look(look_id=content.get('look_id'))
            response = {}
            response['content_type'] = content.get('content_type')
            response['look_title'] = content.get('look_title')
            response['look_id'] = content.get('look_id')
            fields = look_metadata.query.fields
            try:
                filters = look_metadata.query.filters.keys()
                for filter in list(filters):
                    fields.append(filter)
                response['fields'] = fields
            except AttributeError as no_filter:
                response['fields'] = fields

            element_info.append(response)

    return element_info


def parse_sql(sdk):
     sql = sdk.run_query(query_id=15, result_format='sql')
     start = sql.find('FROM')
     finish = sql.find('GROUP')
     from_clause = sql[start:finish]
     split_query = from_clause.split('\n')
     as_query = [line.strip() for line in split_query  if line.strip()[:2] == 'AS']
     response = []
     for line in as_query:
         end = line.find('ON')
         response.append(line[2:end].strip())
     return(response)


def main():
    ini_file = '../ini/looker.ini'

    sdk = looker_sdk.init31(config_file=ini_file)
    
    content_metadata = get_content_id_title(sdk=sdk)
    '''
    Pandas code to create a dataframe, explode the list of fields, split that column into fields and
    views 
    '''
    df = pd.DataFrame(data=find_content_views(looker_content=content_metadata, sdk=sdk))
    df = df.explode(column='fields')
    df[['view', 'field']] = df['fields'].str.split('.', 1, expand=True)
    df = df.drop(['fields'], axis=1)
    # -# Uncomment the next two lines if you want to see views in isolation
    # df = df.drop(['field'], axis=1)
    # df.drop_duplicates(inplace=True)
    ic(df.head(15))
    df.to_csv('output.csv')


if __name__ == "__main__":
    # main()
    ini_file = '../ini/looker.ini'

    sdk = looker_sdk.init31(config_file=ini_file)
    
    ic(parse_sql(sdk=sdk))
