import mysql.connector
import mysql.connector.pooling
import re
import logging


class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(host="localhost", user="root", password="password",
                                                  database="metadatastore")
        self.resources_directory = "src/resources"
        self.create_table_script = f"{self.resources_directory}/create_table.sql"
        self.alter_table_script = f"{self.resources_directory}/alter_table.sql"
        self.procedure_created = False

    def create_table(self, table_name: str, initial_partitions: int):
        with open(self.create_table_script) as script:
            ddl = script.read().format(table_name=table_name).rstrip()
            if initial_partitions > 1:
                end_of_statement = re.compile(r"\);\s*$")
                ddl = end_of_statement.sub(f") PARTITION BY HASH(id) PARTITIONS {initial_partitions};", ddl)
            cursor = self.__cursor()
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                cursor.execute(ddl)
            finally:
                cursor.close()

    def populate_table(self, table_name: str, row_count: int):
        cursor = self.__cursor()
        try:
            data = [(f"hbase_id_{index}", index * 100, "db.database.collection", index % 10, index) for index in range(0, row_count)]
            statement = f"INSERT INTO {table_name} " \
                        f"(hbase_id, hbase_timestamp, topic_name, kafka_partition, kafka_offset) " \
                        f"VALUES (%s, %s, %s, %s, %s)"
            cursor.executemany(statement, data)
            self.connection.commit()
        finally:
            cursor.close()

    def alter_table(self, table_name: str, required_partitions: int):
        self.__create_procedure()
        cursor = self.__cursor()
        try:
            for result in cursor.callproc("alter_reconciliation_table", [table_name, required_partitions]):
                print(f"RESULT: {result}")
        finally:
            cursor.close()

    def partition_count(self, table_name: str) -> int:
        return self.__fetch_count(
            f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.PARTITIONS WHERE TABLE_NAME = '{table_name}'")

    def column_count(self, table_name: str, column_name: str) -> int:
        return self.__fetch_count(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                                  f"WHERE TABLE_NAME = '{table_name}' "
                                  f"AND COLUMN_NAME = '{column_name}'")

    def index_count(self, table_name: str, index_name: str) -> int:
        return self.__fetch_count(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS "
                                  f"WHERE TABLE_NAME = '{table_name}' "
                                  f"AND INDEX_NAME = '{index_name}'")

    def row_count(self, table_name: str) -> int:
        return self.__fetch_count(f"SELECT COUNT(*) FROM {table_name}")

    def __fetch_count(self, sql: str) -> int:
        cursor = self.__cursor()
        try:
            cursor.execute(sql)
            return int(cursor.fetchone()[0])
        finally:
            cursor.close()

    def __create_procedure(self):
        if not self.procedure_created:
            cursor = self.__cursor()
            try:
                with open(self.alter_table_script) as script:
                    for result in cursor.execute(script.read(), multi=True):
                        print(result)
            finally:
                cursor.close()
            self.procedure_created = True

    def __cursor(self):
        return self.connection.cursor()
