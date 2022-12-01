"""
Copyright 2021 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import itertools
from lmanage.sqlparse import parse
from lmanage.sqlparse.sql import IdentifierList, Identifier
from lmanage.sqlparse.tokens import Keyword, DML


def is_subselect(parsed):
    if not parsed.is_group:
        return False
    for item in parsed.tokens:
        if item.ttype is DML and item.value.upper() == 'SELECT':
            return True
    return False


def extract_from_part(parsed):
    from_seen = False
    for item in parsed.tokens:
        if item.is_group:
            for x in extract_from_part(item):
                yield x
        if from_seen:
            if is_subselect(item):
                for x in extract_from_part(item):
                    yield x
            elif item.ttype is Keyword and item.value.upper() in ['ORDER', 'GROUP', 'BY', 'HAVING', 'GROUP BY']:
                from_seen = False
                StopIteration
            else:
                yield item
        if item.ttype is Keyword and item.value.upper() == 'FROM':
            from_seen = True


def extract_table_identifiers(token_stream):
    for item in token_stream:
        if isinstance(item, IdentifierList):
            for identifier in item.get_identifiers():
                value = identifier.value.replace('"', '').lower()
                yield value
        elif isinstance(item, Identifier):
            value = item.value.replace('"', '').lower()
            yield value


def extract_tables(sql):
    # let's handle multiple statements in one sql string
    extracted_tables = []
    statements = list(parse(sql))
    for statement in statements:
        if statement.get_type() != 'UNKNOWN':
            stream = extract_from_part(statement)
            extracted_tables.append(
                set(list(extract_table_identifiers(stream))))
    rough_tables = list(itertools.chain(*extracted_tables))
    rough_tables = [elem.split(' ') for elem in rough_tables]
    clean_list = []
    for elem in rough_tables:
        select = []
        for i in elem:
            if i:
                select.append(i)

        if len(select) < 4:
            clean_list.append(select)

    clean_table = [elem[0].strip('\n')
                   for elem in clean_list if not elem[0].startswith('z__')]
    # print(clean_table)
    return clean_table


if __name__ == '__main__':
    sql = """    
    -- generate derived table source_query_rank
-- Building temporary derived table system__activity::source_query_rank on instance 7ecf10dbe337872a19ea64ca19132ba5
CREATE TEMPORARY TABLE looker_tmp.source_query_rank SELECT
    history.SOURCE  AS `sorted_source`,
    COUNT(CASE WHEN (history.status NOT LIKE 'cache_only_miss' OR history.status IS NULL) THEN 1 ELSE NULL END) AS `query_run_count`
FROM history
WHERE (((
            CONVERT(history.CREATED_AT USING utf8mb4)
            ) >= ((CURDATE())) AND (
            CONVERT(history.CREATED_AT USING utf8mb4)
            ) < ((DATE_ADD(CURDATE(),INTERVAL 1 day))))) AND (history.SOURCE ) IS NOT NULL
GROUP BY
    1
ORDER BY
    COUNT(CASE WHEN (history.status NOT LIKE 'cache_only_miss' OR history.status IS NULL) THEN 1 ELSE NULL END) DESC
-- finished source_query_rank => looker_tmp.source_query_rank
SELECT
    (DATE_FORMAT(
            CONVERT(history.CREATED_AT USING utf8mb4)
           ,'%Y-%m-%d %H')) AS `history.created_hour`,
    source_query_rank.query_run_count AS `source_query_rank.query_run_count`,
    source_query_rank.sorted_source AS `source_query_rank.sorted_source`,
        (MOD((DAYOFWEEK(
            CONVERT(history.CREATED_AT USING utf8mb4)
           ) - 1) - 1 + 7, 7)) AS `history.created_day_of_week_index`,
        (DATE_FORMAT(
            CONVERT(history.CREATED_AT USING utf8mb4)
           ,'%W')) AS `history.created_day_of_week`,
    COUNT(DISTINCT CASE WHEN (history.status NOT LIKE 'cache_only_miss' OR history.status IS NULL) THEN history.id ELSE NULL END) AS `history.query_run_count`
FROM history
LEFT JOIN looker_tmp.source_query_rank AS source_query_rank ON history.SOURCE = source_query_rank.sorted_source
WHERE (((
            CONVERT(history.CREATED_AT USING utf8mb4)
            ) >= ((CURDATE())) AND (
            CONVERT(history.CREATED_AT USING utf8mb4)
            ) < ((DATE_ADD(CURDATE(),INTERVAL 1 day)))))
GROUP BY
    1,
    2,
    3,
    4,
    5
ORDER BY
    (DATE_FORMAT(
            CONVERT(history.CREATED_AT USING utf8mb4)
           ,'%Y-%m-%d %H')) DESC
LIMIT 5000
    """

    print(extract_tables(sql))
