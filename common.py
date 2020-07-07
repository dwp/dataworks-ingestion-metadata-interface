import logging
import socket
import argparse
import boto3
import os
import sys


def setup_logging(logger_level, environment, application):
    """Set the default logger with json output."""
    the_logger = logging.getLogger()
    for old_handler in the_logger.handlers:
        the_logger.removeHandler(old_handler)

    new_handler = logging.StreamHandler(sys.stdout)

    hostname = socket.gethostname()

    json_format = (
        '{ "timestamp": "%(asctime)s", "log_level": "%(levelname)s", "message": "%(message)s", '
        f'"environment": "{environment}","application": "{application}", '
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
    parser.add_argument("--rds-database-table")  # Has to come from payload job
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

    if "RDS_PASSWORD_SECRET_NAME" in os.environ:
        _args.rds_password_secret_name = os.environ["RDS_PASSWORD_SECRET_NAME"]

    return _args
