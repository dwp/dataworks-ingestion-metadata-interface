import json

from common import *
from database import *


required_message_keys = [
    "table-name",
]

args = get_parameters()
logger = setup_logging(
    os.environ["LOG_LEVEL"] if "LOG_LEVEL" in os.environ else "INFO",
    args.environment,
    args.application,
)


def handler(event, context):
    """Entrypoint in AWS.

    Arguments:
        event (dict): Event from AWS
        context (dict): Context from AWS

    """
    check_or_create_tables(args.rds_table_name)


"""
TODO
Validate the tables schema for any issues and raise exception if found
Create users and grant permissions
"""


def check_or_create_tables(table_name):
    """
    Checks if the database exists then calls off to check if table exists
    """
    check_table_exists_query = f"DESCRIBE {args.rds_database}.{table_name};"

    result = execute_query(check_table_exists_query)
    print(result)
    if result:
        logger.info("Table exists")
    else:
        logger.error("Table doesn't exist")
        raise Exception


def create_database_table(table_name):
    """
    Creates the required metadata store schema
    """

    schema_creation_query = [
        f"CREATE DATABASE {args.rds_database} CHARACTER SET 'utf8';",
        f"USE {args.rds_database};",
    ]

    schema_creation_query.append(get_schema_from_file(f"{table_name}.sql"))

    for command in schema_creation_query:
        execute_query(command)
    logger.info("Database and table created")


def get_schema_from_file(filename):
    """
    Get the SQL instructions to provision the metastore database from file

    :return: a list of each SQL query in the file
    """
    with open(filename, "r") as sql_file:
        queries_list = sql_file.read()
        print(queries_list)
        return queries_list
