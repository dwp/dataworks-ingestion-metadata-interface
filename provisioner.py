from common import *
from database import *
import json


def handler(event, context):
    logger = setup_logging(
        os.environ["LOG_LEVEL"] if "LOG_LEVEL" in os.environ else "INFO",
        os.environ["ENVIRONMENT"],
        os.environ["APPLICATION"],  # TODO: catch key error
    )

    args = get_parameters(event, ["table-name"])

    # create table if not exists
    execute_file("create_table.sql", Table[args["table-name"]])

    # Create user if not exists and grant access
    execute_file("grant_user.sql", Table[args["table-name"]])

    # validate table and users exist and structure is correct
    validate_table(args["rds_database_name"], args["table-name"])


def validate_table(database, table_name):
    # check table exists
    result = execute_query(
        f"SELECT count(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{database}' AND TABLE_NAME = '{table_name}';"
    )
    if result == 0:
        return False

    # check table schema
    table_structure = execute_query(
        f"DESCRIBE {database}.{table_name}"
    )
    print(table_structure)
    # TODO

    return True


if __name__ == "__main__":
    json_content = json.loads(open("event.json", "r").read())
    handler(json_content, None)
