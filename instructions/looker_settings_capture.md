# Looker Instance Object Migrator Tool 
## The tool is opinionated in functionality by not migrating content or settings that are established on a per user basis.

The Looker Object Migrator Tool is an API based CLI tool to capture Looker Objects preserving a point in time snapshot as a text based file. This file can then be version controlled and used to configure or amend existing objects in a Looker instance. 

The advantages of having Looker Objects set out in a text file are numerous, for example: 
- version controlling Looker objects such as content or Folder structure and permissions (or even setting up automated processes such as gitops)
- massively reducing number of clicks required to set up an instance from scratch, or revert an instance back to desired state
- defining one source of truth across multiple looker instances, for instance shards
- having a clearly defined security permission doc that can interact with other services such as SAML.

The Object Migrator Tool is comprised of two commands a capture tool and configure tool. The tools are designed to work in concert, i.e. the configure tool is expecting the output of the capture tool, although it's entirely possible to use them individually.

## Impacted Settings
The Looker Instance settings that are impacted by these tools are: 
- User Attributes (creation and value setting on groups)
- Nested Folder Structure
- Looker Content Access Settings
- User Groups
- User Roles
- User Permission Sets
- User Model Sets
- Looker Content (looks and dashboards)
- Looker Content Schedules and Alerts

## Typical Workflow

1. Run the LManage Capturator commmand to generate a Yaml file [example yaml file](#) 
2. Make sure you understand the existing settings, 
3. Check Yaml file into a version control system of choice
4. Restore Looker system settings using the LManage Configurator command

#### [Capture Tool aka Capturator specific documentation](https://github.com/looker-open-source/lmanage/blob/main/instructions/capturator_README.md)
#### [Configure Tool aka Configurator specific documentation](https://github.com/looker-open-source/lmanage/blob/main/instructions/configurator_README.md)



