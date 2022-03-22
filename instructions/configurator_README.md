# configurator
The mapview command will find the etymology of the content on your dashboard, exporting a CSV that looks like [this](https://docs.google.com/spreadsheets/d/1TzeJW46ml0uzO9RdLOOLxwtvUWjhmZxoa-xq4pbznV0/edit?resourcekey=0-xbWC87hXYFNgy1As06NncA#gid=900312158).

##### example usage
`lmanage configurator --yaml-config-path ./output/my_output.csv --ini-file ~/py/projects/ini/k8.ini`
##### flags
- **path** (`--yaml-config-path`, `-yp`) This is the path to the yaml file to use for instance configuration. 
- **ini-file** (`--ini-file`, `-i`) This is the file path to the ini file that you've created to use the Looker SDK
```
#example Ini file
[Looker_Instance]
base_url=https://looker-dev.company.com:19999 (or 443 if hosted in GCP)
client_id=abc
client_secret=xyz
verify_ssl=True
```
- **level** (`--level`, `-l`) **Optional** Set this flag to DEBUG to receive expanded results in stdout for debugging  

##### yaml configurations
Yaml configurations are set in 3 stages, Roles (which creates model sets and permission sets), Folders (where you can manage view and edit access), and User Attributes (where you can add or remove user attribute and associated values in your)

###### Group Creation
There is no need to specfically create groups, Lmanage will scan for all instances of the team values in the following parameters and create the necessary group names. These groups will be attributed with the parameters that you specify in your yaml file.

###### Roles
###### Example Usage
```
role_BusinessOperations_Develope:
  role: BODevelopers
  permissions:
    - access_data
    - can_see_system_activity
    - see_dashboards
    - clear_cache_refresh
    - create_table_calculations
    - deploy
    - develop
    - download_without_limit
    - explore
    - manage_spaces
    - mobile_app_access
    - save_content
    - schedule_look_emails
    - see_drill_overlay
    - see_lookml
    - see_sql
    - see_user_dashboards
    - send_to_integration 
    - use_sql_runner
  model_set:
    - name: model_set_1
      models:
        - model_1 
        - model_2
  team:
    - BusinessOperations_BO_Dev
    - SpecialTeam
```
The looker `role` title should be prefaced by `role_` as lmanage uses this key to identify that this is a role, the role name can be whatever you want. Looker permissions are intricate and relate to what actions you are able to do on a Looker Instance, please review these links before constructing your [role](https://docs.looker.com/admin-options/settings/roles)

###### Folders
###### Example Usage
```
#####################
# FOLDER PERMISSONS #
#####################
folder_permissions:
  business_operations_folder: 
  - name: 'Business Operations' 
    team_view:
      - BusinessOperations
      - Marketing
    subfolder:
      - name: APAC 
        team_edit:
          - APAC_group
        team_view:
          - RestOfWorld_group 
      - name: 'Rest of World'
        subfolder:
          - name: EMEA
            team_edit:
              - EMEA_group
            team_view:
              - RestOfWorld_group
          - name: USA
            subfolder:
              - name: 'West Region'
                team_edit:
                  - WestRegion_group 
                team_view:
                  - RestOfWorld_group
 
```
Similarly to `role` LManage uses a specific keyphrase `folder_permissions`, to denote an entry with folder permissions. Each folder at the highest level will be nested beneath the `/Shared` folder on Looker. To create a nested folder structure, use the keyword `subfolder`. LManage will then recurse through this nested structure to create each folder and assign appropriate permissions. Folder permissions are attributed using the keywords `team_edit` and `team_view`. If no values are presented then LManage will assume inheritance of the permission of it's parent folder.

####### Important

Please try to understand how folder permissions are inherited in Looker, familiarize yourself with these useful docs. 
- [Looker Docs](https://docs.looker.com/sharing-and-publishing/organizing-spaces)
- [Designing and configuring a system of access levels](https://docs.looker.com/admin-options/tutorials/access-controls)
- [Best Practice, Secure your Folders](https://help.looker.com/hc/en-us/articles/360001897687-Best-Practice-Secure-Your-Spaces-A-Content-Access-Walk-through)

###### User Attributes
###### Example Usage

```
###################
# User Attributes #
###################
# attr_region:
ua_region_all:
  name: region_all
  type: string
  hidden_value: false 
  user_view: true
  user_edit: false
  value:
    - us
    - ag
    - bb
    - dd
  team:
    - Cameos
    - Freddy
    - AudreyGroup
```
User attributes will be created based on their appropriate values you input and assigned to the groups that are present in the team parameter.

**This is not an officially supported Google Product.**
