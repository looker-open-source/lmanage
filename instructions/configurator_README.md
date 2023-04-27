# configurator
The configurator command pushes your content and settings into a new instance. It expects two files that are the format that is exported by the capturator. This tool enables a security model that is controlled from a declarative yaml file, that can be run on a specific cadence to ensure that regardless of instance drift, each time the configurator is run it will reset a Looker and content instance back to the values defined in your Yaml file. To generate the Yaml file it is possible to do so manually but much better to generate this programmatically using the [Capturator command](https://github.com/looker-open-source/lmanage/tree/main/instructions/capturator_README.md) 

##### Example usage
`lmanage configurator --yaml-config-path ./config/my_full_instance_config.yaml --ini-file ~/my_permissions/looker.ini`
##### Flags
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

##### Yaml configurations
Yaml configurations are set in 3 stages, Roles (which creates model sets and permission sets), Folders (where you can manage view and edit access), and User Attributes (where you can add or remove user attribute and associated values in your)

###### Group Creation
There is no need to specfically create groups, Lmanage will scan for all instances of the team values in the following parameters and create the necessary group names. These groups will be attributed with the parameters that you specify in your yaml file.

###### Roles
###### Example Output
```
# PERMISSION SETS
- !LookerPermissionSet
  permissions:
  - access_data
  - download_with_limit
  - explore
  - schedule_look_emails
  - see_looks
  name: test_permission_set

# MODEL SETS
- !LookerModelSet
  models: []
  name: All

# LOOKER ROLES
- !LookerRoles
  permission_set: test
  model_set: All
  teams:
  - BusinessOperations
  - Freddy
  - HugoTesty
  name: test_role
```
In this context, the `name` parameter is analagous to the name of the Looker object, and the `teams` parameter is analagous to a Looker User Group. Please review these links before constructing your [role](https://docs.looker.com/admin-options/settings/roles)

###### Folders
###### Example Output
```
# FOLDER PERMISSONS 
- !LookerFolder
  parent_id:
  id: '1'
  name: Shared
  subfolder:
  - !LookerFolder
    parent_id: '1'
    id: '147'
    name: suffering succotash
    subfolder:
    - !LookerFolder
      parent_id: '147'
      id: '148'
      name: another_one
      subfolder:
      - !LookerFolder
        parent_id: '148'
        id: '150'
        name: ps_allhands
        subfolder: []
        content_metadata_id: '151'
        team_edit:
        - ps_allhand2
        - HugoTesty
        team_view:
        - ps_allhand1
      - !LookerFolder
        parent_id: '148'
        id: '149'
        name: sharkytesttest
        subfolder: []
        content_metadata_id: '150'
        team_edit:
        - new_group
        - HugoTesty
        team_view:
        - nick
      content_metadata_id: '149'
      team_edit:
      - new_group
      - HugoTesty
      team_view:
      - ps_allhand2
      - ps_allhand1
      - newer_group
    content_metadata_id: '148'
    team_edit: []
    team_view:
    - new_group
    - ps_allhand2
    - ps_allhand1
    - newer_group
  content_metadata_id: '1'
  team_edit: []
  team_view:
  - All Users
```
Each folder at the highest level will be nested beneath the `/Shared` folder on Looker. To see where a nested folder structure exists, the keyword `subfolder` is used. Folder permissions are attributed using the keywords `team_edit` and `team_view`. If no values are presented then LManage Capturator will assume inheritance of the permission of it's parent folder. The above folder structure can be represented as:
.
└── Shared Folder/
    └── suffering_succotash Folder/
        └── another_one Folder/
            ├── sharkytesttest Folder!
            └── another_one

###### Important

Please try to understand how folder permissions are inherited in Looker, familiarize yourself with these useful docs. 
- [Looker Docs](https://cloud.google.com/looker/docs/organizing-spaces)
- [Designing and configuring a system of access levels](https://docs.looker.com/admin-options/tutorials/access-controls)
- [Best Practice, Secure your Folders](https://help.looker.com/hc/en-us/articles/360001897687-Best-Practice-Secure-Your-Spaces-A-Content-Access-Walk-through)

###### User Attributes
###### Example output

```
# USER_ATTRIBUTES
- !LookerUserAttribute
  name: city
  uatype: string
  hidden_value: false
  user_view: 'True'
  user_edit: 'False'
  default_value: '%'
  teams:
  - london team: ericlyons
  - new york team: New York
  - safetyfirst: least_privilege
```
The user attribure parameters are synonomous with the existing Looker UI controls with the exception that `teams` represent user groups and are represented as a key/value pair.  

###### Important

Please try to understand how USER_ATTRIBUTES are utilized and referenced in Looker and they are super powerful and dangerous, familiarize yourself with these useful docs. 
- [User Attribute Looker Docs](https://cloud.google.com/looker/docs/admin-panel-users-user-attributes#:~:text=Looker%20automatically%20includes%20some%20user,but%20should%20not%20be%20deleted.)


**This is not an officially supported Google Product.**
