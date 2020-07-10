from common import *
from database import *
import json
import os


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

    # TODO: Validate args
    correlation_id = args["correlation-id"]
    topic_name = ""

    connection = get_connection()

    # create table if not exists
    query = f"SELECT * FROM {Table[args['table-name']].value} WHERE correlation_id = '{correlation_id}'"
    if bool(topic_name):
        query += f" AND topic_name = '{topic_name}'"
    result = execute_query(query, connection)

    connection.close()

    return result


if __name__ == "__main__":
    json_content = json.loads(open("event.json", "r").read())
    handler(json_content, None)
