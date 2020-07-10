from common import *
from database import *
import json
import os
import re


def handler(event, context):
    try:
        setup_logging(
            os.environ["LOG_LEVEL"] if "LOG_LEVEL" in os.environ else "INFO",
            os.environ["ENVIRONMENT"],
            os.environ["APPLICATION"],
        )
    except KeyError as e:
        print(
            f"CRITICAL failed to configure logging, environment variable {e.args[0]} missing"
        )
        raise e

    args = get_parameters(event, ["table-name", "correlation-id"])

    # Validate args
    args_valid = True
    if not validate_arg(args["correlation-id"]):
        logger.error(f"Required argument 'correlation-id' has an invalid value of: {args['correlation-id']}")
        args_valid = False

    topic_name = None
    if "topic-name" in args:
        if validate_arg(args["topic-name"]):
            topic_name = args["topic-name"]
        else:
            logger.error(f"Optional argument 'topic-name' has an invalid value of: {args['topic-name']}")
            args_valid = False

    if not args_valid:
        raise ValueError("Arguments passed to handler failed to validate")

    connection = get_connection()

    # create table if not exists
    query = f"SELECT * FROM {Table[args['table-name']].value} WHERE correlation_id = '{args['correlation-id']}'"
    if bool(topic_name):
        query += f" AND topic_name = '{topic_name}'"
    result = execute_query(query, connection)

    connection.close()

    return result


def validate_arg(string):
    pattern = re.compile(r"^[\da-zA-Z_\-.]*$")
    return bool(pattern.fullmatch(string))


if __name__ == "__main__":
    json_content = json.loads(open("event.json", "r").read())
    handler(json_content, None)
