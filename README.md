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

## Fields Returneds

- **dashboard_id**, the id of the looker dashboard 	
- **element_id**, the id of the visualization element on the looker dashboard	
- **sql_joins**, the joins used in a query grouped by element id	
- **fields_used**, the fields used by the query grouped by element id
- **sql_table_name**, the underlying sql value being referenced at the view level of the lookml (assuming the view is standard)	
- **potential_join**, for the explore that powers the element query, what are all the potential joins available	
- **used_joins**, 	
- **used_view_names**,	
- **unused_joins**,
