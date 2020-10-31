#!/usr/bin/env python3

import unittest
from unittest import mock

from query_lambda import query


class TestQuery(unittest.TestCase):
    @mock.patch("common.database.Table")
    @mock.patch("common.common.get_table_name")
    @mock.patch("query_lambda.query.logger")
    def test_query_generates_correctly_with_no_optional_parameters(
        self, logger_mock, get_table_name_mock, table_mock
    ):
        table_name = "test-table"
        table_mock.return_value = [table_name]
        get_table_name_mock.return_value = table_name
        args = {"table-name": table_name}
        expected = (
            "SELECT hbase_id, hbase_timestamp, CAST(write_timestamp AS char) AS write_timestamp, "
            + "correlation_id, topic_name, kafka_partition, kafka_offset, "
            + f"reconciled_result, CAST(reconciled_timestamp AS char) AS reconciled_timestamp FROM {table_name};"
        )
        actual = query.build_query(args)

        self.assertEqual(expected, actual)

    @mock.patch("common.database.Table")
    @mock.patch("common.common.get_table_name")
    @mock.patch("query_lambda.query.logger")
    def test_query_generates_correctly_with_one_optional_parameter(
        self, logger_mock, get_table_name_mock, table_mock
    ):
        table_name = "test-table"
        table_mock.return_value = [table_name]
        get_table_name_mock.return_value = table_name
        args = {"hbase-id-like": "test", "table-name": table_name}
        expected = (
            "SELECT hbase_id, hbase_timestamp, CAST(write_timestamp AS char) AS write_timestamp, "
            + "correlation_id, topic_name, kafka_partition, kafka_offset, "
            + f"reconciled_result, CAST(reconciled_timestamp AS char) AS reconciled_timestamp FROM {table_name} WHERE hbase_id LIKE '%test%';"
        )
        actual = query.build_query(args)

        self.assertEqual(expected, actual)

    @mock.patch("common.database.Table")
    @mock.patch("common.common.get_table_name")
    @mock.patch("query_lambda.query.logger")
    def test_query_generates_correctly_with_two_optional_parameters(
        self, logger_mock, get_table_name_mock, table_mock
    ):
        table_name = "test-table"
        table_mock.return_value = [table_name]
        get_table_name_mock.return_value = table_name
        args = {
            "hbase-id-equals": "test",
            "correlation-id-equals": "test2",
            "table-name": table_name,
        }
        expected = (
            "SELECT hbase_id, hbase_timestamp, CAST(write_timestamp AS char) AS write_timestamp, "
            + "correlation_id, topic_name, kafka_partition, kafka_offset, "
            + f"reconciled_result, CAST(reconciled_timestamp AS char) AS reconciled_timestamp FROM {table_name} WHERE hbase_id = 'test' AND correlation_id = 'test2';"
        )
        actual = query.build_query(args)

        self.assertEqual(expected, actual)

    @mock.patch("common.database.Table")
    @mock.patch("common.common.get_table_name")
    @mock.patch("query_lambda.query.logger")
    def test_query_generates_correctly_with_two_optional_parameters_and_ignored_other_parameters(
        self, logger_mock, get_table_name_mock, table_mock
    ):
        table_name = "test-table"
        table_mock.return_value = [table_name]
        get_table_name_mock.return_value = table_name
        args = {
            "hbase-id-like": "test",
            "correlation-id-equals": "test2",
            "test-id-equals": "test2",
            "table-name": table_name,
        }
        expected = (
            "SELECT hbase_id, hbase_timestamp, CAST(write_timestamp AS char) AS write_timestamp, "
            + "correlation_id, topic_name, kafka_partition, kafka_offset, "
            + f"reconciled_result, CAST(reconciled_timestamp AS char) AS reconciled_timestamp FROM {table_name} WHERE hbase_id LIKE '%test%' AND correlation_id = 'test2';"
        )
        actual = query.build_query(args)

        self.assertEqual(expected, actual)

    @mock.patch("common.database.Table")
    @mock.patch("common.common.get_table_name")
    @mock.patch("query_lambda.query.logger")
    def test_query_generates_correctly_with_two_optional_parameters_of_different_type(
        self, logger_mock, get_table_name_mock, table_mock
    ):
        table_name = "test-table"
        table_mock.return_value = [table_name]
        get_table_name_mock.return_value = table_name
        args = {
            "hbase-id-like": "test",
            "kafka-partition-equals": "1",
            "table-name": table_name,
        }
        expected = (
            "SELECT hbase_id, hbase_timestamp, CAST(write_timestamp AS char) AS write_timestamp, "
            + "correlation_id, topic_name, kafka_partition, kafka_offset, "
            + f"reconciled_result, CAST(reconciled_timestamp AS char) AS reconciled_timestamp FROM {table_name} WHERE hbase_id LIKE '%test%' AND kafka_partition = 1;"
        )
        actual = query.build_query(args)

        self.assertEqual(expected, actual)

    @mock.patch("common.database.Table")
    @mock.patch("common.common.get_table_name")
    @mock.patch("query_lambda.query.logger")
    def test_query_generates_correctly_with_two_optional_parameters_using_or_comparison_method(
        self, logger_mock, get_table_name_mock, table_mock
    ):
        table_name = "test-table"
        table_mock.return_value = [table_name]
        get_table_name_mock.return_value = table_name
        args = {
            "hbase-id-like": "test",
            "kafka-partition-equals": "1",
            "query-connector-type": "OR",
            "table-name": table_name,
        }
        expected = (
            "SELECT hbase_id, hbase_timestamp, CAST(write_timestamp AS char) AS write_timestamp, "
            + "correlation_id, topic_name, kafka_partition, kafka_offset, "
            + f"reconciled_result, CAST(reconciled_timestamp AS char) AS reconciled_timestamp FROM {table_name} WHERE hbase_id LIKE '%test%' OR kafka_partition = 1;"
        )
        actual = query.build_query(args)

        self.assertEqual(expected, actual)

    @mock.patch("common.database.Table")
    @mock.patch("common.common.get_table_name")
    @mock.patch("query_lambda.query.logger")
    def test_query_generates_correctly_with_three_optional_parameters(
        self, logger_mock, get_table_name_mock, table_mock
    ):
        table_name = "test-table"
        table_mock.return_value = [table_name]
        get_table_name_mock.return_value = table_name
        args = {
            "hbase-id-like": "test",
            "kafka-partition-equals": "1",
            "correlation-id-equals": "test2",
            "table-name": table_name,
        }
        expected = (
            "SELECT hbase_id, hbase_timestamp, CAST(write_timestamp AS char) AS write_timestamp, "
            + "correlation_id, topic_name, kafka_partition, kafka_offset, "
            + f"reconciled_result, CAST(reconciled_timestamp AS char) AS reconciled_timestamp FROM {table_name} WHERE hbase_id LIKE '%test%' AND correlation_id = 'test2' AND kafka_partition = 1;"
        )
        actual = query.build_query(args)

        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
