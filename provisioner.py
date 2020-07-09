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

    connection = get_connection()

    # create table if not exists
    execute_statement(
        open("create_table.sql")
        .read()
        .format(table_name=Table[args["table-name"]].value),
        connection,
    )

    # Create user if not exists and grant access
    execute_multiple_statements(
        open("grant_user.sql")
        .read()
        .format(table_name=Table[args["table-name"]].value),
        connection,
    )

    # validate table and users exist and structure is correct
    validate_table(
        args["rds_database_name"], Table[args["table-name"]].value, connection
    )

    connection.close()


def validate_table(database, table_name, connection):
    # check table exists
    result = execute_query(
        f"SELECT count(*) FROM INFORMATION_SCHEMA.TABLES "
        f"WHERE TABLE_SCHEMA = '{database}' "
        f"AND TABLE_NAME = '{table_name}';",
        connection,
    )
    if result == 0:
        return False

    # check table schema
    table_structure = execute_query_to_dict(
        f"DESCRIBE {database}.{table_name}", connection
    )
    print(table_structure)
    # TODO

    return True


if __name__ == "__main__":
    json_content = json.loads(open("event.json", "r").read())
    handler(json_content, None)
