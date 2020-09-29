from common import common, database
import json
import os
import re


logger = None


queryable_fields = [
    ["hbase_id", "hbase-id-equals", "=", "string"],
    ["hbase_id", "hbase-id-like", "LIKE", "string"],
    ["hbase_timestamp", "hbase-timestamp-equals", "=", "int"],
    ["correlation_id", "correlation-id-equals", "=", "string"],
    ["topic_name", "topic-name-equals", "=", "string"],
    ["kafka_partition", "kafka-partition-equals", "=", "int"],
    ["kafka_offset", "kafka-offset-equals", "=", "int"],
    ["reconciled_result", "reconciled-result-equals", "=", "int"],
]


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

    # Validate args
    args_valid = True
    if "topic-name" in args:
        if not validate_arg(args["topic-name"]):
            logger.error(
                f"Optional argument 'topic-name' has an invalid value of: {args['topic-name']}"
            )
            args_valid = False

    if not args_valid:
        raise ValueError("Arguments passed to handler failed to validate")

    connection = database.get_connection()
    query = build_query(args)
    result = database.execute_query(query, connection)

    connection.close()

    return result


def build_query(args):
    query_connector_type = (
        args["query-connector-type"].upper()
        if "query-connector-type" in args
        else "AND"
    )

    query = f"SELECT * FROM {common.get_table_name(args)}"

    queryable_options = []
    for queryable_field in queryable_fields:
        if queryable_field[1] in args:
            field_name = queryable_field[0]
            value_to_check = args[queryable_field[1]]
            comparison_operator = queryable_field[2]
            field_type = queryable_field[3]
            if field_type in ["string"]:
                value_to_check = f"'{value_to_check}'"
            queryable_options.append(
                f"{field_name} {comparison_operator} {value_to_check}"
            )

    if len(queryable_options) > 0:
        query += f" WHERE {queryable_options[0]}"
        if len(queryable_options) > 1:
            for count in range(1, len(queryable_options)):
                query += f" {query_connector_type} {queryable_options[count]}"

    return query


def validate_arg(string):
    pattern = re.compile(r"^[\da-zA-Z_\-.]*$")
    return bool(pattern.fullmatch(string))


if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    rel_path = "../resources"
    abs_file_path = os.path.join(script_dir, rel_path)

    json_content = json.loads(
        open(os.path.join(abs_file_path, "event.json"), "r").read()
    )
    handler(json_content, None)
