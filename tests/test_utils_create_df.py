#!/usr/bin/python
#
# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pandas as pd
import lmanage.utils.create_df as create_df


def test_create_df(mocker):
    data = [
        {'content_type': 'dashboard', 'title': 'user Test',
            'dash_elem_id': '4', 'content_id': '1', 'tables': ['order_items']},
        {'content_type': 'dashboard', 'title': 'user Test',
            'dash_elem_id': '46', 'content_id': '1', 'tables': ['order_items']},
        {'content_type': 'dashboard', 'title': 'user Test',
            'dash_elem_id': '33', 'content_id': '20', 'tables': 'No Content'},
        {'content_type': 'dashboard', 'title': 'user Test',
            'dash_elem_id': '42', 'content_id': '20', 'tables': ['order_items']},
        {'content_type': 'dashboard', 'title': 'user Test',
            'dash_elem_id': '32', 'content_id': '21', 'tables': ['order_items']},
        {'content_type': 'dashboard', 'title': 'test', 'dash_elem_id': '44',
            'content_id': '23', 'tables': ['order_items']},
        {'content_type': 'dashboard', 'title': 'test', 'dash_elem_id': '45',
            'content_id': '23', 'tables': 'No Content'},
        {'content_type': 'dashboard', 'title': 'broken_content',
            'dash_elem_id': '43', 'content_id': '25', 'tables': ['order_items']},
        {'content_type': 'look', 'title': 'test',
            'content_id': 1, 'tables': ['order_items']},
        {'content_type': 'look', 'title': 'lookwsched',
            'content_id': 2, 'tables': ['order_items']},
        {'content_type': 'look', 'title': 'lookwsched',
            'content_id': 19, 'tables': ['order_items']},
        {'content_type': 'look', 'title': 'lookwsched',
            'content_id': 20, 'tables': 'No Content'},
        {'content_type': 'look', 'title': '1',
            'content_id': 21, 'tables': ['user']},
        {'content_type': 'look', 'title': 'broken_content',
            'content_id': 22, 'tables': ['order_items']},
        {'content_type': 'look', 'title': 'ttt', 'content_id': 23, 'tables': ['order_items']}]
    response = create_df.create_df(
        data=data)
    assert isinstance(response, pd.DataFrame)


def test_create_df_string(mocker):
    data = '''[
        {
            "content_usage.last_accessed_date": "2021-02-16",
            "content_usage.content_id": "5",
            "content_usage.content_title": "5",
            "content_usage.content_type": "look"
        },
        {
            "content_usage.last_accessed_date": "2021-02-13",
            "content_usage.content_id": "2",
            "content_usage.content_title": "2",
            "content_usage.content_type": "dashboard"
        },
        {
            "content_usage.last_accessed_date": "2021-02-11",
            "content_usage.content_id": "1",
            "content_usage.content_title": "test",
            "content_usage.content_type": "look"
        }
    ]
    '''
    response = create_df.create_df(
        data=data)
    assert isinstance(response, pd.DataFrame)
