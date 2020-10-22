from common import common, database, common_query
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
    if "topic-name" in args and not validate_arg(args["topic-name"]):
        logger.error(
            f"Optional argument 'topic-name' has an invalid value of: {args['topic-name']}"
        )
        args_valid = False

    if not args_valid:
        raise ValueError("Arguments passed to handler failed to validate")

    logger.info("Getting connection to database")
    connection = database.get_connection()

    logger.info("Building query")
    query = build_query(args)

    logger.info("Getting connection to database")
    result = database.execute_query_to_dict(query, connection)

    connection.close()

    return result


def build_query(args):
    global logger

    query_connector_type = (
        args["query-connector-type"].upper()
        if "query-connector-type" in args
        else "AND"
    )

    query = (
        "SELECT hbase_id, hbase_timestamp, CAST(write_timestamp AS char) AS write_timestamp, "
        + "correlation_id, topic_name, kafka_partition, kafka_offset, "
        + f"reconciled_result, CAST(reconciled_timestamp AS char) AS reconciled_timestamp FROM {common.get_table_name(args)}"
    )

    queryable_options = common_query.get_queryable_options(queryable_fields, args)

    if len(queryable_options) > 0:
        query += f" WHERE {queryable_options[0]}"
        if len(queryable_options) > 1:
            for count in range(1, len(queryable_options)):
                query += f" {query_connector_type} {queryable_options[count]}"

    query += ";"

    logger.info(f'Query built as "{query}"')
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
