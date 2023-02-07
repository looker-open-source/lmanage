# Looker Instance Settings Capture and Configurations

The Looker Capturator and Configurator are API based CLI tools to capture Looker security based settings and preserve a point in time snapshot as a text based file. This file can then be used to configure or amend existing settings in a Looker instance. 

The advantages of having your security permissioning set out in a text file are numerous, for example: 
- version controlling your security updates (or even setting up automated processes such as gitops)
- massively reducing number of clicks required to set up an instance from scratch, or revert an instance back to desired state
- defining one source of truth across multiple looker instances, for instance shards
- having a clearly defined security permission doc that can interact with other services such as SAML.

The tools are designed to work in concert although it's entirely possible to use them individually.

## Impacted Settings
The Looker Instance settings that are impacted by these tools are: 
- User Attributes (creation and value setting on groups)
- Nested Folder Structure
- Looker Content Access Settings
- User Groups
- User Roles
- User Permission Sets
- User Model Sets

The tool purposely does not affect settings on a per user basis. This is an opinionated choice because I believe that everyone in a large Looker deployment should fit into a group of some sort. It's incredibly easy to have security protocol drift when deviating from a ratified plan because of 'feature testing'.

## Typical Workflow

1. Run the LManage Capturator commmand to generate a Yaml file [example yaml file](#) 
2. Make sure you understand the existing settings, 
3. Check Yaml file into a version control system of choice
4. Restore Looker system settings using the LManage Configurator command

#### [Capturator specific documentation](https://github.com/looker-open-source/lmanage/blob/main/instructions/capturator_README.md)
#### [Configurator specific documentation](https://github.com/looker-open-source/lmanage/blob/main/instructions/configurator_README.md)



