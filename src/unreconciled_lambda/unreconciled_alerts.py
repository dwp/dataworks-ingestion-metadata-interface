from common import common, database, common_query
import os

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

    logger.info("Building unreconciled_after_max_age_query")
    query = unreconciled_after_max_age_query(args)

    logger.info("Getting connection to database")
    result = database.execute_query_to_dict(query, connection)

    connection.close()

    return result

def unreconciled_after_max_age_query(args):
    global logger

    query_connector_type = (
        args["query-connector-type"].upper()
        if "query-connector-type" in args
        else "AND"
    )

    max_age_scale = args["RECONCILER_MAXIMUM_AGE_SCALE"]
    max_age_unit = args["RECONCILER_MAXIMUM_AGE_UNIT"]

    max_timestamp = max_age_scale + " " + max_age_unit

    query = (
            "SELECT * "
            f"FROM {common.get_table_name(args)} "
            "WHERE reconciled_result = false "
            f"AND write_timestamp > {max_timestamp}"
    )

    queryable_options = common_query.get_queryable_options(args, queryable_fields)

    if len(queryable_options) > 0:
        query += f" WHERE {queryable_options[0]}"
        if len(queryable_options) > 1:
            for count in range(1, len(queryable_options)):
                query += f" {query_connector_type} {queryable_options[count]}"

    query += ";"

    logger.info(f'Query built as "{query}"')

    return query
