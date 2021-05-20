# Lmanage
## What is it.
LManage is a collection of useful tools for [Looker](https://looker.com/) admins to help curate and cleanup content and it's associated source [LookML](https://docs.looker.com/data-modeling/learning-lookml/what-is-lookml).

LManage will ultimately have many different commands.
### Commands

#### help and version
```
lmanage --help
Usage: lmanage [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  mapview
```
#### mapview
The mapview command will find the etymology of the content on your dashboard, exporting a CSV that looks like [this](https://docs.google.com/spreadsheets/d/1TzeJW46ml0uzO9RdLOOLxwtvUWjhmZxoa-xq4pbznV0/edit?resourcekey=0-xbWC87hXYFNgy1As06NncA#gid=900312158).

##### example usage
`lmanage mapview --path ./output/my_output.csv --ini-file ~/py/projects/ini/k8.ini --project /test_lookml_files/the_look -table "order_items"`
##### flags
- _path_ (`--path`, `-fp`) This is the path where you would like the outputfile for your returned dataset to be. 
- _ini_file_ (`--ini-file`, `-i`) This is the file path to the ini file that you've created to use the Looker SDK
(example Ini file)
```
[Looker_Instance]
base_url=https://looker-dev.company.com:19999 (or 443 if hosted in GCP)
client_id=abc
client_secret=xyz
verify_ssl=True
```
- _project_ (`--project`, `-p`) This is the file path to your local project of LookML files that lmanage will scan to associate connections between your Looker content and LookML
Lmanage can either return a full dataset of all content mapping, or a prefiltered dataset with all content associated with a specific table or field.
- _table_ (`--table`, `-t`) Expecting input of lookml view name
- _field_ (`--field`, `-f`) Expecting input of fully scoped LookML field name e.g. viewname.fieldname 

## Fields Returneds

- **dashboard_id**, the id of the looker dashboard 	
- **element_id**, the id of the visualization element on the looker dashboard	
- **sql_joins**, the joins used in a query grouped by element id	
- **fields_used**, the fields used by the query grouped by element id
- **sql_table_name**, the underlying sql value being referenced at the view level of the lookml (assuming the view is standard)	
- **potential_join**, for the explore that powers the element query, what are all the potential joins available	
- **used_joins**, joins used by the underlying queries obtained by parsing sql of query 	
- **used_view_names**, views that are used by each query grouped by element_id	
- **unused_joins**, views that are unused by the specific query of the dashboard element
