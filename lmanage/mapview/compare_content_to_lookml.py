import ast
import coloredlogs
import logging
from lmanage.mapview.utils import parse_lookml

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')
logging.getLogger("looker_sdk").setLevel(logging.WARNING)


def format_str_list(list_str):
    new_list = ast.literal_eval(list_str)
    return new_list


def collate_view_files(parsed_lookml):
    response = []
    for instance_lookml in parsed_lookml:
        for path in instance_lookml.keys():
            if 'view.lkml' in path:
                response.append(instance_lookml)
    return response


def extract_field_names_from_lookml(parsed_lookml, data_storage):

    try:
        dimensions = parsed_lookml['dimensions']
    except KeyError:
        dimensions = []
        logger.warning('no dimensions present in view')
    try:
        measures = parsed_lookml['measures']
    except KeyError:
        measures = []
        logger.warning('no measures present in view')

    view_name = parsed_lookml.get('name')
    for dim in dimensions:
        field_name = dim.get('name')
        full_name = f'{view_name}.{field_name}'
        data_storage[full_name] = view_name

    for meas in measures:
        if len(meas) > 0:
            field_name = meas.get('name')
            full_name = f'{view_name}.{field_name}'
            data_storage[full_name] = view_name

    return data_storage


def match_fields_to_lookml(field_list, lookml):
    matched_fields = []
    for field in field_list:
        match = lookml.get(field, 'no match')
        if match != 'no match':
            matched_fields.append(field)

    return matched_fields


def extract_view_from_field(field_name):
    view_name = field_name.split('.')[0]
    return view_name


def create_lookml_field_lookup(view_file):
    field_lookup = {}
    for lookml in view_file:
        parsed_lookml = parse_lookml.LookML(lookml)
        if parsed_lookml.has_views():
            for v in parsed_lookml.views():
                extract_field_names_from_lookml(
                    parsed_lookml=v, data_storage=field_lookup)
    return field_lookup


def create_viewname_lookup(view_file):
    sql_table_name_list = []
    for lookml in view_file:
        parsed_lookml = parse_lookml.LookML(lookml)
        if parsed_lookml.has_views():
            for v in parsed_lookml.views():
                try:
                    sql_table_name = v['sql_table_name']
                    sql_table_name_list.append(sql_table_name)
                except KeyError:
                    logger.warning('no sql_table_name present in view')
    return sql_table_name_list


def match_element_to_lookml(instancedata, view_file):
    field_lookup = create_lookml_field_lookup(view_file)
    viewname_lookup = create_viewname_lookup(view_file)

    matches = []
    for dashboard in instancedata:
        fields_used = format_str_list(dashboard.get('query.formatted_fields'))
        views_in_dash = []
        for field in fields_used:
            x = extract_view_from_field(field)
            if x not in views_in_dash:
                views_in_dash.append(x)
        matched_fields = match_fields_to_lookml(field_list=fields_used,
                                                lookml=field_lookup)

        for views in viewname_lookup:
            if views not in views_in_dash:
                views_in_dash.append(views)

        temp = {}
        temp['used_views'] = views_in_dash
        temp['matched_fields'] = matched_fields
        temp['dashboard'] = dashboard['dashboard.id']
        temp['element_id'] = dashboard['dashboard_element.id']
        matches.append(temp)
    print(matches)
    return matches
