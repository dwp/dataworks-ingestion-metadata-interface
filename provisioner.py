from common import *
from database import *


def handler(event, context):
    logger = setup_logging(
        os.environ["LOG_LEVEL"] if "LOG_LEVEL" in os.environ else "INFO",
        os.environ["ENVIRONMENT"],
        os.environ["APPLICATION"],  # TODO: catch key error
    )

    args = get_parameters(event, ["table-name"])

    # create table (if not exist)
    execute_file('create_table.sql', Table[args['table-name']])

    # grant access to table
    execute_file('grant_user.sql', Table[args['table-name']])

    # validate table exists and structure is correct
    # validate users exist


def validate_table(database, table_name):
    # check table exists
    result = execute_query(
        f"""
        SELECT count(*) 
        FROM information_schema.TABLES 
        WHERE (TABLE_SCHEMA = `{database}`) AND (TABLE_NAME = `{table_name}`)
        """
    )
    if result == 0:
        return False

    # check table schema
    # TODO

    return True
