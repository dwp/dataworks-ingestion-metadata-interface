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
    args.application
)


def handler(event, context):
    """Entrypoint in AWS.

    Arguments:
        event (dict): Event from AWS
        context (dict): Context from AWS

    """
    payload_config = get_wrapped_message(event)
    table_name = payload_config['table-name']

    check_or_create_schema(mysqlclient, table_name)

    check_users_exist(mysqlclient)


def get_wrapped_message(event):
    """Check the mandatory keys and wrap them.

    Arguments:
        event (dict): Event from AWS

    """
    sns_message = event["Records"][0]["Sns"]
    dumped_message = get_escaped_json_string(sns_message)
    logger.debug(f'Getting wrapped message", "sns_message": {dumped_message}, "mode": "wrapping')
    payload_message = json.loads(sns_message["Message"])
    dumped_payload = get_escaped_json_string(payload_message)
    logger.info(f'Received sns", "payload_message": {dumped_payload}, "mode": "wrapping')

    missing_keys = []
    for required_message_key in required_message_keys:
        if required_message_key not in payload_message:
            missing_keys.append(required_message_key)

    if missing_keys:
        bad_keys = ", ".join(missing_keys)
        error_message = f"Required keys are missing from payload: {bad_keys}"
        raise KeyError(error_message)

    table_name = payload_message["table-name"]

    return {"table-name": table_name}


def get_escaped_json_string(json_dict):
    """Dump out the given json string with escaped quotes.

    Arguments:
        json_dict (Dict): Parsed json as a dictionary

    """
    try:
        escaped_string = json.dumps(json.dumps(json_dict))
    except Exception:
        escaped_string = json.dumps(json_dict)

    return escaped_string


def mysql_query(mysql_connector, sql_query):
    connection = mysql_connector.connect(
        host=args.rds_hostname,
        port=args.rds_port,
        user=args.rds_username,
        password=args.rds_password,
        charset="utf8",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
        connection.commit()

        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            result = cursor.fetchall()
            return result

    except Exception as e:
        logger.error(f'Failed to query database", "query": "{sql_query}"')
        raise e

    finally:
        connection.close()


def mysql_execute(mysql_connector, sql_execute_query):
    connection = mysql_connector(
        host=args.rds_hostname,
        port=args.rds_port,
        user=args.rds_username,
        password=args.rds_password,
        database="",
        charset="utf8",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_execute_query)
        connection.commit()

    except Exception as e:
        logger.warn(
            f'Failed to execute query against database", "query": "{sql_execute_query}'
        )

    finally:
        connection.close()


def check_or_create_schema(mysql_connector, tablename):
    """
    Checks if the database exists then calls off to check if table exists
    """
    list_databases_query = "SHOW DATABASES;"

    results = mysql_query(mysqlclient, list_databases_query)

    resultant_query_match = {"Database": args.rds_database}

    if resultant_query_match in results:
        logger.info("Database exists, checking if table exists")
        check_table_exists(mysql_connector, args.rds_database, tablename)
    else:
        logger.info("Database doesn't exist, creating it now")
        create_database_schema(mysql_connector, args.rds_database, tablename)


def check_table_exists(mysql_connector, database_name, table_name):
    check_table_exists_query = f"DESCRIBE {database_name}.{table_name};"

    result = mysql_query(mysql_connector, check_table_exists_query)
    if result:
        logger.info("Table exists")
    else:
        logger.error("Table doesn't exist")
        raise Exception


def create_database_schema(mysql_connector, database_name, table_name):
    """
    Creates the required metadata store schema
    """
    schema_creation_query = [
        f"CREATE DATABASE {args.rds_database} CHARACTER SET 'utf8';",
        f"USE {args.rds_database};"
    ]

    schema_creation_query.append(get_schema_from_file(f"{table_name}.sql"))

    for command in schema_creation_query:
        mysql_execute(mysql_connector, schema_creation_query)
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

