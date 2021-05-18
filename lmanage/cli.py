import click
from lmanage import delinquent_user
from lmanage import get_content_with_views
from lmanage import delinquent_content
from lmanage import validate_content


@click.group()
@click.version_option()
def lmanage():
    pass


# @lmanage.command()
# @click.option("-d", "--days", help="How many days has the user to be removed been inactive for")
# @click.option("-i", "--ini-file", help="Path to the ini file to use for sdk authentication")
# @click.option("-rm", "--removeuser", help="disable user in instance", default=False)
# @click.option("--csv", help="export your delinquent user into a csv", default=False)
# def removeuser(**kwargs):
#     delinquent_user.main(**kwargs)


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


# @lmanage.command()
# @click.option("-d", "--days", help="How many days has the user to be removed been inactive for")
# @click.option("-i", "--ini-file", help="Path to the ini file to use for sdk authentication")
# @click.option("-b", "--backup-location", help="file path where you would like backed up content to live")
# def dcontent(**kwargs):
#     delinquent_content.main(**kwargs)


# @lmanage.command()
# @click.option("-bd", "--broken-dash-id", help="Helper content to send out unique message related to content")
# @click.option("-bl", "--broken-look-id", help="Helper content to send out unique message related to content")
# @click.option("-i", "--ini-file", help="Path to the ini file to use for sdk authentication")
# @click.option("-b", "--backup-url", help="gzr instance that you should input for back up (the machine name in your .netrc file)")
# def broke_content(**kwargs):
#     validate_content.main(**kwargs)
