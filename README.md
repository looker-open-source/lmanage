# Lmanage
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
| Live    | [mapview](https://github.com/looker-open-source/lmanage/tree/main/instructions/mapview_README.md) | Find the LookML fields and tables that are associated with a piece of Looker content                          |
| Live    | [capturator](https://github.com/looker-open-source/lmanage/tree/main/instructions/looker_settings_capture.md)| Capture your Looker Instance Group, Folder, Role and User Attributes into a Yaml based Config File |
| Live    | [configurator](https://github.com/looker-open-source/lmanage/tree/main/instructions/looker_settings_capture.md)| Configure your Looker Instance Group, Folder, Role and User Attributes via a Yaml based Config File |
| Planned | removeuser | Based on last time logged in, prune Looker users to ensure a performant, compliant Looker instance                                                                                                   |
| Planned | dcontent   | Iterate through an input of content, delete content and back it up using [gzr](https://github.com/looker-open-source/gzr) for easy restoration                                                                                               |
| Planned | bcontent   | Iterate through all broken content (using content validator) and email a customized message to each dashboard owner                                                                                  |
| Planned | scoper     | Takes in a model file, elminates the * includes, iterate through the explores and joins and creates a fully scoped model include list for validation performance and best practice code organization |

#### help and version
```
lmanage --help
Usage: lmanage [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  mapview
  capturator
  configurator
```
#### mapview
The mapview command will find the etymology of the content on your dashboard, exporting a CSV that looks like [this](https://docs.google.com/spreadsheets/d/1TzeJW46ml0uzO9RdLOOLxwtvUWjhmZxoa-xq4pbznV0/edit?resourcekey=0-xbWC87hXYFNgy1As06NncA#gid=900312158).

[instructions](https://github.com/looker-open-source/lmanage/tree/main/instructions/mapview_README.md)

#### configurator
The configurator command will allow you to manage your Looker security and access settings from a simple text based Yaml file. This file can be version controlled and productionalized using a gitops workflow.

[instructions](https://github.com/looker-open-source/lmanage/tree/main/instructions/looker_settings_capture.md)

#### capturator
The capturator command will allow you to restore your Looker security and access settings from a simple text based Yaml file. This file can be version controlled and productionalized using a gitops workflow.

[instructions](https://github.com/looker-open-source/lmanage/tree/main/instructions/looker_settings_capture.md)


**This is not an officially supported Google Product.**
