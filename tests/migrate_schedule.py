import looker_sdk
import os
import json
from lmanage.datetime import datetime
from lmanage.typing import Callable, List

ini = '/usr/local/google/home/hugoselbie/code_sample/py/ini/k8.ini'
# os.environ["LOOKERSDK_BASE_URL"] = "https://profservices.dev.looker.com:19999" #If your looker URL has .cloud in it (hosted on GCP), do not include :19999 (ie: https://your.cloud.looker.com).
# os.environ["LOOKERSDK_API_VERSION"] = "3.1" #3.1 is the default version. You can change this to 4.0 if you want.
# os.environ["LOOKERSDK_VERIFY_SSL"] = "true" #Defaults to true if not set. SSL verification should generally be on unless you have a real good reason not to use it. Valid options: true, y, t, yes, 1.
# os.environ["LOOKERSDK_TIMEOUT"] = "120" #Seconds till request timeout. Standard default is 120.

# #Get the following values from lmanage.your Users page in the Admin panel of your Looker instance > Users > Your user > Edit API keys. If you know your user id, you can visit https://your.looker.com/admin/users/<your_user_id>/edit.
# os.environ["LOOKERSDK_CLIENT_ID"] =  "xxxxx" #No defaults.
# os.environ["LOOKERSDK_CLIENT_SECRET"] = "xxxxx" #No defaults. This should be protected at all costs. Please do not leave it sitting here, even if you don't share this document.

sdk = looker_sdk.init31(config_file=ini)
print('Looker SDK 3.1 initialized successfully.')

# How to define old user..
# User hasn't logged in for n_days based on credentials_email or credentials_saml
n_days = 60

# function to calculate number of days between last log in date and current date


def days_between(d1: datetime, d2: datetime) -> int:
    """Return abs difference in days between two timestamps"""
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

# function to get a list of the old users


def fetch_old_users(n_days: int, exclude_email: bool = True, exclude_saml: bool = True):
    """Fetch all users who haven't logged in for more than n_days"""
    users = sdk.all_users(
        fields='id,email,credentials_email(logged_in_at),credentials_saml(logged_in_at)')
    if exclude_email:
        users = [u for u in users
                 if u.get('credentials_email') is not None
                 ]
    inactive_email = [u for u in users
                      if u['credentials_email']['logged_in_at'] != None
                      and days_between(
                          u['credentials_email']['logged_in_at'].split('T')[0],
                          str(datetime.today()).split()[0]
                      ) > n_days
                      ]
    if exclude_saml:
        users = [u for u in users
                 if u.get('credentials_saml') is not None
                 ]
    inactive_saml = [u for u in users
                     if u['credentials_saml']['logged_in_at'] != None
                     and days_between(
                         u['credentials_saml']['logged_in_at'].split('T')[0],
                         str(datetime.today()).split()[0]
                     ) > n_days
                     ]
    user_id_inactive_email = [u.id for u in inactive_email]
    user_id_inactive_saml = [u.id for u in inactive_saml]
# Check if user id is in email list and if not then merge saml list user ids into email list
    for x in user_id_inactive_saml:
        if x not in user_id_inactive_email:
            user_id_inactive_email.append(x)
    return user_id_inactive_email


user_list = fetch_old_users(n_days)
print(user_list)

# For testing purposes
# ids 236,18,758
# names - alejandro@looker.com, jon.bale@looker.com, jcarnes+profservices@google.com
user_list = [236, 18, 758]
new_owner_id = 11

# Find all schedules of a particular user id


def find_schedules(current_owner_id: int):
    result = {}
    scheduled_plans = sdk.all_scheduled_plans(user_id=current_owner_id)
    for i in scheduled_plans:
        result[i['name']] = i['id']
    return result

# Transfer all schedules of a user to a new user.


def update_owner(current_owner_id: int, new_owner_id: int):
    body = {}
    body['user_id'] = new_owner_id
    find = find_schedules(current_owner_id)
    for i in find.values():
        sdk.update_scheduled_plan(i, body)
    return body

# Loop through list of users to find schedules and transfer schedules


def transfer_schedule(user_list: list, create_user: False):
    # find old users
    old_user_list = fetch_old_users(n_days=1)
    # find their schedules
    for user in old_user_list:
        x = find_schedules(user)
        print(x)
        update_owner(user, 2)
    # find reassign them to meta user
    # do i need to create meta user
    # if create_user:
    #     sd
    # update owner
#
#     update_owner(u, new_owner_id)

#   return f'Schedule transferred for {user_list}'


if __name__ == "__main__":
    reassign_schedules = transfer_schedule(user_list)
    print(reassign_schedules)

# from lmanage.pprint import pprint
# import snoop - then @snoop
