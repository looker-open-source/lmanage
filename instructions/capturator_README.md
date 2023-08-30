# capturator

The capturator is the instance capture portion of the Instance Migrator Tool. It's use is to generate a point in time representation of a Looker instance settings and content and preserve a representation of those objects as a Yaml file that can be used by the configurator command to provision your instance. The tool will generate two yaml files that will be created in the folder of your choice, the value you enter as your `config-dir` for Looker settings and a file appended with `content`, for referencing the Looker content to be transitioned.

##### Example usage

`lmanage capturator --ini-file ~/my_permissions/looker.ini  --config-dir ./config`

##### Flags

- **config-dir** (`--config-dir`, `-cd`) This is the directory to generate the yaml files to use for instance configuration.
- **ini-file** (`--ini-file`, `-i`) **Optional** This is the file path to the ini file that you've created to use the Looker SDK. Will default to environment variables if not set.

```
#example Ini file
[Looker_Instance]
base_url=https://looker-dev.company.com:19999 (or 443 if hosted in GCP)
client_id=abc
client_secret=xyz
verify_ssl=True
```

- **level** (`--verbose`, `-v`) **Optional** Set this flag to receive expanded results in stdout for debugging
- **force** (`--force`, `-f`) **Optional** Flag to skip initial confirmation, defaults to False

##### Anatomy of your Settings Yaml File

###### Roles

###### Example Output From File

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

```
Shared Folder
├── suffering_succotash Folder
│   ├── another_one Folder
│   │   ├── sharkytesttest Folder
│   │   ├── another_one

```

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

###### Content

###### Example Output From File

```
# LookData
- !LookObject
  legacy_folder_id: '302'
  look_id: '2112'
  title: Look_Title
  query_obj:
    model: thelook
    view: order_items
    fields:
    - users.count
    pivots:
    fill_fields:
    filters:
    filter_expression:
    sorts:
    - order_items.created_year desc
    - users.count desc
    limit: '500'
    column_limit: '50'
    total:
    row_total:
    subtotals:
    vis_config:
      type: single_value
      show_single_value_title: true
      show_comparison: false
      comparison_type: value
      comparison_reverse_colors: false
      show_comparison_label: true
      colors:
      - '#5245ed'
      - '#a2dcf3'
      - '#776fdf'
      - '#1ea8df'
      - '#49cec1'
      - '#776fdf'
      - '#49cec1'
      - '#1ea8df'
      - '#a2dcf3'
      - '#776fdf'
      - '#776fdf'
      - '#635189'
      color_palette: Default
      hidden_fields: []
      y_axes: []
    filter_config:
    visible_ui_sections:
    dynamic_fields: '[]'
    query_timezone: America/Los_Angeles
  description: ''
# Dashboard Content
- !DashboardObject
  legacy_folder_id: '81'
  lookml: "- dashboard: new_dashboard\n  title: New Dashboard\n  layout: newspaper\n\
    \  preferred_viewer: dashboards-next\n  description: ''\n  preferred_slug: SkRfx99hbJYDPBuNXZRsdi\n\
    \  elements:\n  - title: Untitled\n    name: Untitled\n    model: system__activity\n\
    \    explore: field_usage\n    type: table\n    fields: [field_usage.field]\n\
    \    limit: 500\n    row:\n    col:\n    width:\n    height:\n"
  dashboard_id: '7'
```

The content.yaml file is generated automatically inside of the `config-dir` and stores the export from looks and dashboards in the instance you're running the capturator against.

The dashboard is stored in lookml and can be amended here (e.g. changing model name or explore name) if desired.

**This is not an officially supported Google Product.**
