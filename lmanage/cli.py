import click
from lmanage import delinquent_user
from lmanage import getContentWithViews
from lmanage import delinquent_content
from lmanage import validate_content


@click.group()
@click.version_option()
def lmanage():
    pass


@lmanage.command()
@click.option("-d", "--days", help="How many days has the user to be removed been inactive for")
@click.option("-i", "--ini-file", help="Path to the ini file to use for sdk authentication")
@click.option("-rm", "--removeuser", help="disable user in instance", default=False)
@click.option("--csv", help="export your delinquent user into a csv", default=False)
def removeuser(**kwargs):
    delinquent_user.main(**kwargs)


@lmanage.command()
@click.option("-f", "--file-path", help="input your file path to save a csv of results")
@click.option("-i", "--ini-file", help="Path to the ini file to use for sdk authentication")
def mapview(**kwargs):
    getContentWithViews.main(**kwargs)


@lmanage.command()
@click.option("-d", "--days", help="How many days has the user to be removed been inactive for")
@click.option("-i", "--ini-file", help="Path to the ini file to use for sdk authentication")
@click.option("-b", "--backup-location", help="file path where you would like backed up content to live")
def dcontent(**kwargs):
    delinquent_content.main(**kwargs)


@lmanage.command()
@click.option("-bd", "--broken-dash-id", help="Helper content to send out unique message related to content")
@click.option("-bl", "--broken-look-id", help="Helper content to send out unique message related to content")
@click.option("-i", "--ini-file", help="Path to the ini file to use for sdk authentication")
@click.option("-b", "--backup-url", help="gzr instance that you should input for back up (the machine name in your .netrc file)")
def broke_content(**kwargs):
    validate_content.main(**kwargs)
