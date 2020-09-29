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
    script_dir = os.path.dirname(__file__)
    rel_path = "AmazonRootCA1.pem"
    abs_file_path = os.path.join(script_dir, rel_path)

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
    connection.commit()


def execute_multiple_statements(sql, connection):
    cursor = connection.cursor()
    results = cursor.execute(sql, multi=True)
    for result in results:
        if result.with_rows:
            logger.debug("Executed: {}".format(result.statement))
        else:
            logger.debug(
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
    cursor = connection.cursor()
    cursor.execute(sql)
    desc = cursor.description
    column_names = [col[0] for col in desc]
    data = [dict(zip(column_names, row)) for row in cursor.fetchall()]
    connection.commit()
    result = {}
    if index_column == "":
        index_column = column_names[0]
    for item in data:
        result[item[index_column]] = item
    return result
