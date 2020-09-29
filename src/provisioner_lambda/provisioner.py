from common import common, database
import json
import os


logger = None


def handler(event, context):
    global logger

    try:
        logger = common.setup_logging(
            os.environ["LOG_LEVEL"] if "LOG_LEVEL" in os.environ else "INFO",
            os.environ["ENVIRONMENT"],
            os.environ["APPLICATION"],
        )
    except KeyError as e:
        print(
            f"CRITICAL failed to configure logging, environment variable {e.args[0]} missing"
        )
        raise e

    args = common.get_parameters(event, ["table-name"])

    connection = database.get_connection()

    # create table if not exists
    database.execute_statement(
        "DROP TABLE {table_name}".format(table_name=common.get_table_name(args)),
        connection,
    )

    script_dir = os.path.dirname(__file__)
    rel_path = "../resources"
    abs_file_path = os.path.join(script_dir, rel_path)

    database.execute_statement(
        open(os.path.join(abs_file_path, "create_table.sql"))
        .read()
        .format(table_name=common.get_table_name(args)),
        connection,
    )

    # Create user if not exists and grant access
    database.execute_multiple_statements(
        open(os.path.join(abs_file_path, "grant_user.sql"))
        .read()
        .format(table_name=common.get_table_name(args)),
        connection,
    )

    # validate table and users exist and structure is correct
    table_valid = validate_table(
        args["rds_database_name"], common.get_table_name(args), connection
    )

    connection.close()

    if not table_valid:
        raise RuntimeError(f"Schema is invalid in table: {common.get_table_name(args)}")


def validate_table(database_name, table_name, connection):
    global logger

    # check table exists
    result = database.execute_query(
        f"SELECT count(*) FROM INFORMATION_SCHEMA.TABLES "
        f"WHERE TABLE_SCHEMA = '{database_name}' "
        f"AND TABLE_NAME = '{table_name}';",
        connection,
    )
    if result == 0:
        return False

    # check table schema
    table_structure = database.execute_query_to_dict(
        f"DESCRIBE {database_name}.{table_name}", connection, "Field"
    )

    int_field_type = "int(11)"
    column_structure_required = {
        "id": {"Field": "id", "Type": int_field_type, "Null": "NO", "Key": "PRI"},
        "hbase_id": {
            "Field": "hbase_id",
            "Type": "varchar(2048)",
            "Null": "YES",
            "Key": "MUL",
            "Default": None,
        },
        "hbase_timestamp": {
            "Field": "hbase_timestamp",
            "Type": "bigint(20)",
            "Null": "YES",
            "Key": "",
            "Default": None,
        },
        "write_timestamp": {
            "Field": "write_timestamp",
            "Type": "datetime",
            "Null": "YES",
            "Key": "MUL",
            "Default": "CURRENT_TIMESTAMP",
        },
        "correlation_id": {
            "Field": "correlation_id",
            "Type": "varchar(1024)",
            "Null": "YES",
            "Key": "",
            "Default": None,
        },
        "topic_name": {
            "Field": "topic_name",
            "Type": "varchar(1024)",
            "Null": "YES",
            "Key": "",
            "Default": None,
        },
        "kafka_partition": {
            "Field": "kafka_partition",
            "Type": int_field_type,
            "Null": "YES",
            "Key": "",
            "Default": None,
        },
        "kafka_offset": {
            "Field": "kafka_offset",
            "Type": int_field_type,
            "Null": "YES",
            "Key": "",
            "Default": None,
        },
        "reconciled_result": {
            "Field": "reconciled_result",
            "Type": "tinyint(1)",
            "Null": "NO",
            "Key": "MUL",
            "Default": "0",
        },
        "reconciled_timestamp": {
            "Field": "reconciled_timestamp",
            "Type": "datetime",
            "Null": "YES",
            "Key": "",
            "Default": None,
        },
    }

    table_valid = True
    for column_name in column_structure_required:
        if column_name in table_structure.keys():
            correct_subvalues = column_structure_required[column_name]
            result_subvalues = table_structure[column_name]

            for key, value in correct_subvalues.items():
                if key in result_subvalues and result_subvalues[key] != value:
                    logger.error(
                        f"{column_name}.{key} is incorrect: expected {value}, found {result_subvalues[key]}."
                    )
                    table_valid = False
        else:
            logger.error(f"{database_name}.{table_name} is missing column: {column_name}")
            table_valid = False

        logger.debug(f"{column_name} column has the correct schema settings.")

    if table_valid:
        logger.info(f"Table {table_name} schema is valid")
    return table_valid


if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    rel_path = "../resources"
    abs_file_path = os.path.join(script_dir, rel_path)

    json_content = json.loads(
        open(os.path.join(abs_file_path, "event.json"), "r").read()
    )
    handler(json_content, None)
