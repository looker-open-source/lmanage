input_data = {'role_BusinessOperations_Developer':
              {'role': 'BODevelopers',
               'permissions': ['access_data', 'use_sql_runner'],
               'model_set': [{'name': 'lk1_test_set', 'models': ['test', 'test2']}],
               'team': ['BusinessOperations_BO_Dev']},
              'folder_permissions':
              {'business_operations_folder': [
                  {'name': 'Business Operations',
                   'team_view': ['Snaptest'],
                   'subfolder': [{'name': 'test_sub', 'team_edit': ['Freddy'], 'team_view': ['hugo']},
                                 {'name': 'test_sub2',
                                  'subfolder':
                                  [{'name': 'test_sub_sub',
                                    'team_edit': ['Famke'],
                                    'team_view': ['hugle']},
                                   {'name': 'subdiddy',
                                    'subfolder': [{'name': 'hugle_testy', 'team_edit': ['Freddy'], 'team_view': ['hugle']}]}]}]}],

               'ua_region_all':
               {'name': 'region_all',
                'type': 'string',
                'hidden_value': 'false',
                'user_view': 'true',
                'user_edit': 'false',
                'value': ['us', 'ag', 'bb', 'dd'],
                'team': ['Cameos', 'Freddy', 'AudreyGroup']}}}


class MockSDK():
    def search_folders(self):
        pass

    def create_folder(self):
        pass

    def search_groups(self):
        pass

    def create_group(self):
        pass


class MockSearchGroup():
    def __init__(self, group_name):
        self.group_name = group_name


class MockCreateGroup():
    def __init__(self, id, name):
        self.id = id
        self.name = name


class MockSearchFolder():
    def __init__(self, parent_id, name, id):
        self.parent_id = parent_id
        self.name = name
        self.id = id


class MockCreateFolder():
    def __init__(self, id, name, content_metadata_id):
        self.id = id
        self.name = name
        self.content_metadata_id = content_metadata_id
