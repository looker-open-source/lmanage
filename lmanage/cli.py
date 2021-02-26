import click
from lmanage import delinquent_user
from lmanage import getContentWithViews
# from lmanage import delinquent_content


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


# @lmanage.command()
# @click.option("-d", "--days", help="How many days has the user to be removed been inactive for")
# @click.option("-i", "--ini-file", help="Path to the ini file to use for sdk authentication")
# @click.option("-ct", "--content-type", help="What type of delinquent content")
# def delinquentcontent(**kwargs):
#     delinquentcontent.main(**kwargs)
