import json
import sys
import os

sys.path.append("..")

from common import common, database, common_query  # noqa: E402

logger = None

queryable_fields = common_query.get_queryable_fields()


def handler(event, _):
    global logger

    logger = common.initialise_logger()

    args = common.get_parameters(
        event,
        ["table-name", "reconciler_maximum_age_scale", "reconciler_maximum_age_unit"],
    )

    logger.info("Getting connection to database")
    connection = database.get_connection()

    logger.info("Querying for unreconciled records after max age")
    query_unreconciled_after_max_age(connection, args)

    logger.info("Querying for reconciled and unreconciled counts")
    query_reconciled_and_unreconciled_counts(connection, args)

    connection.close()


def query_unreconciled_after_max_age(connection, args):
    query = unreconciled_after_max_age_query(args)
    logger.info(f'Executing query for unreconciled after max age", "query": "{query}')
    results = database.execute_query_to_dict(query, connection)

    if results is not None:
        logger.info(
            f'Got results for unreconciled records after max age", "results_size": "{len(results)}'
        )
        for result in results.items():
            logger.info(
                f'Unreconciled record message after max age", "record": "{result}'
            )
    else:
        logger.info("Results returned with None value")


def unreconciled_after_max_age_query(args):
    global logger

    query_connector_type = (
        args["query-connector-type"].upper()
        if "query-connector-type" in args
        else "AND"
    )

    max_age_scale = args["reconciler_maximum_age_scale"]
    max_age_unit = args["reconciler_maximum_age_unit"]

    query = (
        "SELECT * "
        f"FROM {common.get_table_name(args)} "
        "WHERE reconciled_result = false "
        f"AND write_timestamp < CURRENT_TIMESTAMP - INTERVAL {max_age_scale} {max_age_unit}"
    )

    queryable_options = common_query.get_queryable_options(args, queryable_fields)

    if len(queryable_options) > 0:
        query += f" WHERE {queryable_options[0]}"
        if len(queryable_options) > 1:
            for count in range(1, len(queryable_options)):
                query += f" {query_connector_type} {queryable_options[count]}"

    query += ";"

    logger.info(f'unreconciled_after_max_age_query", "query": "{query}')

    return query


def query_reconciled_and_unreconciled_counts(connection, args):
    query = reconciled_and_unreconciled_counts_query(args)
    logger.info(
        f'Executing query for reconciled and unreconciled record counts", "query": "{query}'
    )
    result = database.execute_query_to_dict(query, connection, "reconciled_result")

    if result is not None:
        logger.info(f'Got result", "result": "{result}')
        unreconciled_count = result.get(0).get("total")
        reconciled_count = result.get(1).get("total")
        logger.info(
            f'Got result for reconciled and unreconciled records", "unreconciled_count": "{unreconciled_count}, '
            f'"reconciled_count": "{reconciled_count}'
        )
    else:
        logger.info("Result returned with None value")


def reconciled_and_unreconciled_counts_query(args):
    global logger

    query_connector_type = (
        args["query-connector-type"].upper()
        if "query-connector-type" in args
        else "AND"
    )

    query = (
        "SELECT COUNT(*) as total, reconciled_result "
        f"FROM {common.get_table_name(args)} "
        "GROUP BY reconciled_result "
    )

    queryable_options = common_query.get_queryable_options(args, queryable_fields)

    if len(queryable_options) > 0:
        query += f" WHERE {queryable_options[0]}"
        if len(queryable_options) > 1:
            for count in range(1, len(queryable_options)):
                query += f" {query_connector_type} {queryable_options[count]}"

    query += ";"

    logger.info(f'reconciled_and_unreconciled_counts_query", "query": "{query}')

    return query


if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    rel_path = "../resources"
    abs_file_path = os.path.join(script_dir, rel_path)

    json_content = json.loads(
        open(os.path.join(abs_file_path, "event.json"), "r").read()
    )
    handler(json_content, None)
