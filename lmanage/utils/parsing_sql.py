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
import sqlparse

from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML


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
    statements = list(sqlparse.parse(sql))
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
    sql = """WITH order_user_sequence_facts AS (select oi.user_id,oi.id as order_id,row_number() over(partition by oi.user_id order by oi.created_at asc ) as order_sequence,
        oi.created_at,
        MIN(oi.created_at) OVER(PARTITION BY oi.user_id) as first_ordered_date,
        LAG(oi.created_at) OVER (PARTITION BY oi.user_id ORDER BY oi.created_at asc) as previous_order_date,
        LEAD(oi.created_at) OVER(partition by oi.user_id ORDER BY oi.created_at) as next_order_date,
        DATEDIFF(DAY,CAST(oi.created_at as date),CAST(LEAD(oi.created_at) over(partition by oi.user_id ORDER BY oi.created_at) AS date)) as repurchase_gap
      from order_items oi
 )
SELECT * FROM (
SELECT *, DENSE_RANK() OVER (ORDER BY z___min_rank) as z___pivot_row_rank, RANK() OVER (PARTITION BY z__pivot_col_rank ORDER BY z___min_rank) as z__pivot_col_ordering, CASE WHEN z___min_rank = z___rank THEN 1 ELSE 0 END AS z__is_h
ighest_ranked_cell FROM (
SELECT *, MIN(z___rank) OVER (PARTITION BY "order_user_sequence_facts.created_at_month") as z___min_rank FROM (
SELECT *, RANK() OVER (ORDER BY "order_user_sequence_facts.created_at_month" DESC, z__pivot_col_rank) AS z___rank FROM (
SELECT *, DENSE_RANK() OVER (ORDER BY "users.gender" NULLS LAST) AS z__pivot_col_rank FROM (
SELECT
    users.gender  AS "users.gender",
        (TO_CHAR(DATE_TRUNC('month', CONVERT_TIMEZONE('UTC', 'America/New_York', order_user_sequence_facts.created_at )), 'YYYY-MM')) AS "order_user_sequence_facts.created_at_month",
    COUNT(DISTINCT order_user_sequence_facts.user_id ) AS "order_user_sequence_facts.count"
FROM public.order_items  AS order_items
INNER JOIN public.users  AS users ON order_items.user_id = users.id
LEFT JOIN public.inventory_items  AS inventory_items ON inventory_items.id = order_items.inventory_item_id
LEFT JOIN order_user_sequence_facts ON users.id = order_user_sequence_facts.user_id
WHERE (order_user_sequence_facts.order_sequence = 1
    )
GROUP BY
    (DATE_TRUNC('month', CONVERT_TIMEZONE('UTC', 'America/New_York', order_user_sequence_facts.created_at ))),
    1) ww
) bb WHERE z__pivot_col_rank <= 16384
) aa
) xx
) zz
 WHERE (z__pivot_col_rank <= 50 OR z__is_highest_ranked_cell = 1) AND (z___pivot_row_rank <= 500 OR z__pivot_col_ordering = 1) ORDER BY z___pivot_row_rank
    """

    print(extract_tables(sql))
    # tables = ', '.join(extract_tables(sql))
    # print('Tables: {}'.format(tables))
