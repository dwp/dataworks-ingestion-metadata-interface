import boto3

import json


class LambdaUtility:

    def __init__(self):
        self.client = boto3.client("lambda", use_ssl=False, endpoint_url="http://localstack:4566")

    def alter_table(self, table_name: str, partition_count: int):
        return self.client.invoke(FunctionName="ingestion-metadata-provisioner",
                                  Payload=self.__payload(table_name, partition_count))

    @staticmethod
    def __payload(table_name: str, partition_count: int) -> bytes:
        return json.dumps({
            "table-name": table_name,
            "partition-count": partition_count,
            "rds_username": "root",
            "rds_password": "password",
            "rds_database_name": "metadatastore",
            "rds_endpoint": "metadatastore",
            "environment": "local",
            "application": "ingestion-metadata-provisioner",
            "rds_password_secret_name": "phony",
            "skip_ssl": True
        }).encode("ASCII")
