import boto3
import base64
import os
import mysql.connector
import mysql.connector.pooling
import logging
import ast
from enum import Enum

logger = logging.getLogger(__name__)

class Table(Enum):
    UCFS = "ucfs"
    EQUALITIES = "equalities"


def get_mysql_password():
    secrets_manager = boto3.client("secretsmanager")
    get_secret_value_response = secrets_manager.get_secret_value(
        SecretId=os.environ["RDS_PASSWORD_SECRET_NAME"]
    )["SecretString"]
    dict = ast.literal_eval(get_secret_value_response) # convert str representation of dict to actual dict
    return dict


def get_connection():
    return mysql.connector.connect(
        host=os.environ["RDS_ENDPOINT"],
        user=os.environ["RDS_USERNAME"],
        password=get_mysql_password(),
        database=os.environ["RDS_DATABASE_NAME"],
        # ssl_ca="AmazonRootCA1.pem",
        # ssl_verify_cert=True,
    )


def execute_statement(sql, connection=get_connection()):
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    connection.close()


def execute_query(sql, connection=get_connection()):
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    connection.commit()
    connection.close()
    return result


def execute_file(filename, sql_parameters, connection=get_connection()):
    sql = open(filename).read()
    cursor = connection.cursor()
    for result in cursor.execute(sql, sql_parameters, multi=True):
        if result.with_rows:
            logger.debug("Executed: {}".format(result.statement))
        else:
            logger.debug(
                "Executed: {}, Rows affected: {}".format(
                    result.statement, result.rowcount
                )
            )

    connection.commit()
    connection.close()
