# LManage
## What is it.
LManage is a collection of useful tools for [Looker](https://looker.com/) admins to help curate and cleanup content and it's associated source [LookML](https://docs.looker.com/data-modeling/learning-lookml/what-is-lookml).

## How do i Install it.
Lmanage can be found on [pypi](#).
```
pip install lmanage
```

## How do I Use it.
### Commands
LManage will ultimately will have many different commands as development continues 
| Status  | Command    | Rationale                                                                                                                                                                                            |
|---------|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Live | Object Migrator Tool | Migrate Looker Objects such as Content, Folders and Permissions, User Groups, Roles and Attributes between a Looker Instance or for Version Control [instructions](https://github.com/looker-open-source/lmanage/tree/main/instructions/looker_settings_capture.md)                                                                                                |
| Planned | scoper     | Takes in a model file, elminates the * includes, iterate through the explores and joins and creates a fully scoped model include list for validation performance and best practice code organization |
| Planned | removeuser | Based on last time logged in, prune Looker users to ensure a performant, compliant Looker instance                                                                                                   |
| Planned | [mapview](https://github.com/looker-open-source/lmanage/tree/main/instructions/mapview_README.md) | Find the LookML fields and tables that are associated with a piece of Looker content                          |

#### help and version
```
lmanage --help
Usage: lmanage [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  capturator
  configurator
```
#### Looker Object Migrator
The object migrator allows you to preserve a point in time representation of your Looker content (Looks and Dashboards), Folder structure, Content access settings, User groups, User roles, User Attributes and preserve these as a Yaml file. This tool then lets you configure a new instance based on that Yaml file.

[instructions](https://github.com/looker-open-source/lmanage/tree/main/instructions/looker_settings_capture.md)


**This is not an officially supported Google Product.**
