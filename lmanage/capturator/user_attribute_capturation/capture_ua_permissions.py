from lmanage.utils import looker_object_constructors as loc, errorhandling as eh, logger_creation as log_color
from tqdm import tqdm
from tenacity import retry, wait_fixed, wait_random, stop_after_attempt

class ExtractUserAttributes():
    def __init__(self,  sdk, logger):
        self.sdk = sdk
        self.logger = logger
        self.user_attribute_metadata = self.existing_user_attributes()
        self.all_group_metadata = self.all_group_metadatas()
    
    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def get_all_user_attributes(self) -> dict:
        response = self.sdk.all_user_attributes()
        return response

    def existing_user_attributes(self) -> dict:
        ex_ua = self.get_all_user_attributes()
        resp = [ua for ua in ex_ua if not ua.is_system]
        return resp

    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def all_group_metadatas(self):
        response=self.sdk.all_groups()
        return response 

    @retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(5))
    def all_user_attribute_group_value_metadata(self, uaid: int):
        response = self.sdk.all_user_attribute_group_values(uaid)
        return response


    def create_user_attributes(self):
        group_metadata = {
            group.id: group.name for group in self.all_group_metadata}
        response = []
        for ua in tqdm(self.user_attribute_metadata, desc = "User Attribute Capture", unit=" user att", colour="#2c8558"):
            group_assign = self.all_user_attribute_group_value_metadata(uaid=ua.id)
            team_values = []

            for group in group_assign:
                group_name = group_metadata.get(group.group_id)
                teams = {}
                teams[group_name] = group.value
                team_values.append(teams)
            looker_ua = loc.LookerUserAttribute(
                name=ua.name,
                uatype=ua.type,
                hidden_value=ua.value_is_hidden,
                user_view=ua.user_can_view,
                user_edit=ua.user_can_edit,
                default_value=ua.default_value,
                teams_val=team_values
            )
            response.append(looker_ua)
        return response
