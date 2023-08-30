from lmanage.utils import parse_yaml as py, logger_creation as log_color


class LookerConfigReader():
    def __init__(self, config_dir):
        logger_level = 'INFO'  # kwargs.get('verbose')
        logger = log_color.init_logger(__name__, logger_level)
        logger.info(
            '----------------------------------------------------------------------------------------')
        logger.info('parsing yaml file')
        self.settings_yaml = py.Yaml(yaml_path=f'{config_dir}/settings.yaml')
        self.content_yaml = py.Yaml(yaml_path=f'{config_dir}/content.yaml')
        # self.logger = log_color.init_logger(__name__, logger_level)

    def read(self):
        self.config = {
            'folder_metadata': self.settings_yaml.get_metadata('folder_metadata'),
            'permission_set_metadata': self.settings_yaml.get_metadata('permission_set_metadata'),
            'model_set_metadata': self.settings_yaml.get_metadata('model_set_metadata'),
            'role_metadata': self.settings_yaml.get_metadata('role_metadata'),
            'user_attribute_metadata': self.settings_yaml.get_metadata('user_attribute_metadata'),
            'look_metadata': self.content_yaml.get_metadata('look_metadata'),
            'dashboard_metadata': self.content_yaml.get_metadata('dashboard_metadata'),
            #     'board_metadata': self.content_yaml.get_metadata('board_metadata'),
        }

    def get_summary(self):
        config = self.config
        look_scheduled_plan_count = sum(
            [len(l.get('scheduled_plans')) if l.get('scheduled_plans') else 0 for l in config['look_metadata']])
        dashboard_scheduled_plan_and_alert_counts = [(
            len(d.get('scheduled_plans')) if d.get('scheduled_plans') else 0,
            len(d.get('alerts')) if d.get('alerts') else 0)
            for d in config['dashboard_metadata']]
        dashboard_scheduled_plan_count = sum(
            dashboard_scheduled_plan_and_alert_counts[0])
        dashboard_alert_count = sum(
            dashboard_scheduled_plan_and_alert_counts[1])
        return f'''
        {len(config['permission_set_metadata']):<5} permissions
        {len(config['model_set_metadata']):<5} models
        {len(config['role_metadata']):<5} roles
        {len(config['user_attribute_metadata']):<5} user attributes
        {len(config['look_metadata']):<5} looks
        {look_scheduled_plan_count:<5} look scheduled plans
        {len(config['dashboard_metadata']):<5} dashboards
        {dashboard_scheduled_plan_count:<5} dashboard scheduled plans
        {dashboard_alert_count:<5} dashboard alerts
        '''
