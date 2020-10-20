from typing import Sequence

import ast
import logging
import os
from enum import Enum

import boto3
import mysql.connector
import mysql.connector.pooling

logger = logging.getLogger(__name__)


class Table(Enum):
    UCFS = "ucfs"
    EQUALITIES = "equalities"


def get_mysql_password():
    secrets_manager = boto3.client("secretsmanager")
    get_secret_value_response = secrets_manager.get_secret_value(
        SecretId=os.environ["RDS_PASSWORD_SECRET_NAME"]
    )["SecretString"]
    secret_dict = ast.literal_eval(
        get_secret_value_response
    )  # converts str representation of dict to actual dict
    return secret_dict["password"]


def get_connection():
    global logger

    script_dir = os.path.dirname(__file__)
    rel_path = "AmazonRootCA1.pem"
    abs_file_path = os.path.join(script_dir, rel_path)

    logger.info(f"Path to the CR cert is '{abs_file_path}'")

    return mysql.connector.connect(
        host=os.environ["RDS_ENDPOINT"],
        user=os.environ["RDS_USERNAME"],
        password=get_mysql_password(),
        database=os.environ["RDS_DATABASE_NAME"],
        ssl_ca=abs_file_path,
        ssl_verify_cert=("SKIP_SSL" not in os.environ),
    )


def execute_statement(sql, connection):
    cursor = connection.cursor()
    cursor.execute(sql)
    logger.info("Executed: {}".format(sql))
    connection.commit()


def execute_multiple_statements(sql, connection):
    global logger

    cursor = connection.cursor()
    results = cursor.execute(sql, multi=True)
    for result in results:
        if result.with_rows:
            logger.info("Executed: {}".format(result.statement))
        else:
            logger.info(
                "Executed: {}, Rows affected: {}".format(
                    result.statement, result.rowcount
                )
            )
    connection.commit()


def execute_query(sql, connection):
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    connection.commit()
    return result


def call_procedure(connection, procedure_name: str, args: Sequence):
    cursor = connection.cursor()
    result = cursor.callproc(procedure_name, args)
    connection.commit()
    return result


def execute_query_to_dict(sql, connection, index_column=""):
    """
    Execute a single SQL query and return a dict of result rows
    Each dict item will contain a dict of values indexed by column name
    Each row will be indexed by index_column or default to first column name

    :param sql: SQL query to execute
    :param connection: database connection to use
    :param index_column: column name that contains value to use to index dict (default to first column), should be a unique column
    :return:
    """
    global logger

    logger.info(
        f'Executing the sql statement: "{sql}" using index column "{index_column}"'
    )
    cursor = connection.cursor()
    cursor.execute(sql)
    desc = cursor.description
    column_names = [col[0] for col in desc]

    logger.info(f'Retrieved column names: "{column_names}"')
    data = [dict(zip(column_names, row)) for row in cursor.fetchall()]

    logger.info("Retrieved data, committing transaction")
    connection.commit()

    logger.info("Transaction committed, formatting dict of results")
    result = {}
    if index_column == "":
        index_column = column_names[0]
    for item in data:
        result[item[index_column]] = item
    return result
