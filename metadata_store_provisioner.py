from os import environ, path
import os
import sys
import socket
import json
import argparse
import pymysql.cursors
import logging
import boto3

log_level = os.environ["LOG_LEVEL"] if "LOG_LEVEL" in os.environ else "INFO"
secretsmanager = boto3.client("secretsmanager")
mysqlclient = pymysql

required_message_keys = [
    "table-name",
]

# Initialise logging
def setup_logging(logger_level):
    """Set the default logger with json output."""
    the_logger = logging.getLogger()
    for old_handler in the_logger.handlers:
        the_logger.removeHandler(old_handler)

    new_handler = logging.StreamHandler(sys.stdout)

    hostname = socket.gethostname()

    json_format = (
        '{ "timestamp": "%(asctime)s", "log_level": "%(levelname)s", "message": "%(message)s", '
        f'"environment": "{args.environment}","application": "{args.application}", '
        f'"module": "%(module)s", "process":"%(process)s", '
        f'"thread": "[%(thread)s]", "hostname": "{hostname}" }}'
    )

    new_handler.setFormatter(logging.Formatter(json_format))
    the_logger.addHandler(new_handler)
    new_level = logging.getLevelName(logger_level.upper())
    the_logger.setLevel(new_level)

    if the_logger.isEnabledFor(logging.DEBUG):
        # Log everything from boto3
        boto3.set_stream_logger()
        the_logger.debug(f'Using boto3", "version": "{boto3.__version__}')

    return the_logger


def get_parameters():
    """Define and parse command line args."""
    parser = argparse.ArgumentParser(
        description="Provision table structure and create required users for metadata store."
    )

    # Parse command line inputs and set defaults
    parser.add_argument("--aws-profile", default="default")
    parser.add_argument("--aws-region", default="eu-west-2")
    parser.add_argument("--environment", default="NOT_SET", help="Environment value")
    parser.add_argument("--application", default="NOT_SET", help="Application")
    parser.add_argument("--rds-hostname")
    parser.add_argument("--rds-port")
    parser.add_argument("--rds-username")
    parser.add_argument("--rds-database")
    parser.add_argument("--rds-database-table") # Has to come from payload job
    parser.add_argument("--metadatastore-secret-id")
    parser.add_argument("--rds-password")

    _args = parser.parse_args()

    # Override arguments with environment variables where set
    if "AWS_PROFILE" in os.environ:
        _args.aws_profile = os.environ["AWS_PROFILE"]

    if "AWS_REGION" in os.environ:
        _args.aws_region = os.environ["AWS_REGION"]

    if "ENVIRONMENT" in os.environ:
        _args.environment = os.environ["ENVIRONMENT"]

    if "APPLICATION" in os.environ:
        _args.application = os.environ["APPLICATION"]

    if "RDS_HOSTNAME" in os.environ:
        _args.rds_hostname = os.environ["RDS_HOSTNAME"]

    if "RDS_PORT" in os.environ:
        _args.rds_port = int(os.environ["RDS_PORT"])

    if "RDS_USERNAME" in os.environ:
        _args.rds_username = os.environ["RDS_USERNAME"]

    if "RDS_DATABASE" in os.environ:
        _args.rds_database = os.environ["RDS_DATABASE"]

    if "RDS_DATABASE_TABLE" in os.environ:
        _args.rds_database_table = os.environ["RDS_DATABASE_TABLE"]

    if "METASTORE_SECRET_ID" in os.environ:
        _args.metadatastore_secret_id = os.environ["METADATASTORE_SECRET_ID"]

    if "RDS_PASSWORD" in os.environ:
        _args.rds_password = os.environ["RDS_PASSWORD"]

    return _args


args = get_parameters()
logger = setup_logging(log_level)
# RDS_PASSWORD = fetch_rds_password_secret(secretsmanager)


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


def fetch_rds_password_secrets(secretsclient):
    """
    Fetchs the RDS PASSWORD for the RDS USERNAME from Secrets Manager
    """

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=args.metastore_secret_id
        )
    except Exception as e:
        logger.error(e)
    else:
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
        else:
            decoded_binary_secret = base64.b64decode(
                get_secret_value_response["SecretBinary"]
            )

    return result["SecretString"]["password"]


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


def check_users_exist(mysqlconnector):
    users_list = ["datawriter", "datareader", "reconciler"]

    for user in users_list:
        check_users_exist_query = f"SELECT User FROM mysql.user WHERE User = '{user}';"

        result = mysql_query(mysqlconnector, check_users_exist_query)

        resultant_query_match = {"User": user}

        if resultant_query_match in result:
            logger.info(f"User {user} exists - re-granting permissions to be sure")
        else:
            logger.info(f"User {user} doesn't exist")
            create_mysql_user(mysqlconnector, user)


def create_mysql_user(mysqlconnector, user):
    print(f"I would create {user} rn")


if __name__ == "__main__":
    try:
        boto3.setup_default_session(
            profile_name=args.aws_profile, region_name=args.aws_region
        )
        json_content = json.loads(open("../../tests/event.json", "r").read())
        handler(json_content, None)
    except Exception as e:
        logger.error(e)
