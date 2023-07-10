input_data = {
    'permission_sets': {
        'developer': {
            'permissions': ['access_data', 'can_see_system_activity', 'see_dashboards', 'clear_cache_refresh', 'create_table_calculations', 'deploy', 'develop', 'download_without_limit', 'explore', 'manage_spaces', 'mobile_app_access', 'save_content', 'schedule_look_emails', 'see_drill_overlay', 'see_lookml', 'see_sql', 'see_user_dashboards', 'send_to_integration', 'use_sql_runner']},
        'user': {
            'permissions': ['access_data', 'clear_cache_refresh', 'create_table_calculations', 'download_without_limit', 'explore', 'manage_spaces', 'mobile_app_access', 'save_content', 'schedule_look_emails', 'see_drill_overlay', 'see_lookml', 'see_lookml_dashboards', 'see_looks', 'see_sql', 'see_user_dashboards', 'send_to_integration']}},
    'model_sets': {
        'lk1_test_set': {
            'models': ['test', 'test2']},
        'lk4_huggy': {
            'models': ['test', 'test1', 'test2']}},
    'roles': {
        'BusinessOperations_Developer': {
            'permissions_set': 'test_perm1',
            'model_set': 'developer',
            'team': ['BusinessOperations_BO_Dev', 'DrewEdit']},

        'BusinessOperations_User': {
            'permissions': 'user',
            'model_set': 'lk4_huggy',
            'team': ['BusinessOperations', 'Freddy']}},
    'folder_permissions': {
        'business_operations_folder': [{
            'name': 'Business Operations',
            'team_view': ['BusinessOperations', 'Snaptest'],
            'subfolder': [{
                'name': 'test_sub',
                'team_edit': ['Freddy'],
                'team_view': ['hugo']},
                {'name': 'test_sub2',
                 'subfolder': [{
                               'name': 'test_sub_sub',
                               'team_edit': ['Famke'],
                               'team_view': ['hugle']},
                               {'name': 'subdiddy',
                                'subfolder': [{
                                              'name': 'hugle_testy',
                                              'team_edit': ['Freddy'],
                                              'team_view': ['hugle']}]}]}]}],
        'sexy_time_folder': [{
            'name': 'sexy time',
            'team_edit': ['sexy_group1'],
            'team_view': ['sexy_group2'],
            'subfolder': [{
                'name': 'sexy_sub'}]}],
        'suffering_succotash_folder': [{
            'name': 'suffering succotash',
            'team_edit': ['sexy_group1'],
            'team_view': ['sexy_group2'],
            'subfolder': [{
                'name': 'another_one',
                'team_edit': ['sexy_group1', 'new_group'],
                'team_view': ['newer_group']}]}]},
    'user_attributes': {
        'region_all': {
            'type': 'string',
            'hidden_value': 'false',
            'user_view': 'true',
            'user_edit': 'false',
            'value': ['us', 'ag', 'bb', 'dd'],
            'team': ['Cameos', 'Freddy', 'AudreyGroup']},
        'region_testy': {
            'type': 'string',
            'hidden_value': 'false',
            'user_view': 'true',
            'user_edit': 'false',
            'value': ['us', 'ag', 'bb'],
            'team': ['Cameos', 'AudreyGroup']},
        'can_see_hugo': {
            'type': 'string',
            'hidden_value': 'false',
            'user_view': 'true',
            'user_edit': 'false',
            'value': ['No'],
            'team': ['Cameos', 'CanSeeDAUGroup']}}}


fake_permission_set = [
    {'role_name': 'BODevelopers',
     'permission': ['access_data', 'use_sql_runner'],
     'model_set_value': [
         {'name': 'lk1_test_set',
          'models': ['test', 'test2']}],
     'teams': ['BusinessOperations_BO_Dev']}]


class MockSDK():
    def search_folders(self):
        pass

    def create_folder(self):
        pass

    def search_groups(self):
        pass

    def create_group(self):
        pass

    def create_permission_set(self):
        pass

    def search_permission_sets(self):
        pass

    def update_permission_set(self):
        pass

    def all_looks(self):
        pass

    def search_looks(self):
        pass

    def create_look(self):
        pass


class MockAll_look_Response():
    def __init__(self, id, folder):
        self.id = id
        self.folder = folder


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
