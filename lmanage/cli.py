import click
from lmanage import delinquent_user
from lmanage import get_content_with_views
from lmanage import delinquent_content
from lmanage import validate_content


@click.group()
@click.version_option()
def lmanage():
    pass


@lmanage.command()
@click.option("-fp", "--path",
              type=click.Path(exists=True),
              help="input your file path to save a csv of results")
@click.option("-i", "--ini-file",
              help="Path to the ini file to use for sdk authentication")
@click.option("-p", "--project",
              help="Path folder containing your lookml files, often taken using a git pull from your connected lookml project repository")
@click.option("-t", "--table",
              help="Add a view name to search for elements that rely on this view")
@click.option("-f", "--field",
              help="Add a fully scoped fieldname (e.g. view_name.field_name) to return a csv with these values")
def mapview(**kwargs):
    get_content_with_views.main(**kwargs)
