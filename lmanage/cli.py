import click
from lmanage import delinquent_user


@click.group()
@click.version_option()
def lmanage():
    pass


@lmanage.command()
@click.option("-d", "--days", help="How many days has the user to be removed been inactive for")
@click.option("-i", "--ini-file", help="Path to the ini file to use for sdk authentication")
def removeuser(**kwargs):
    delinquent_user.main(**kwargs)
