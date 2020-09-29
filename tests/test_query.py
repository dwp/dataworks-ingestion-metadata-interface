#!/usr/bin/env python3

import json
import pytest
import unittest
from unittest import mock
from query_lambda import query


class TestQuery(unittest.TestCase):
    @mock.patch("common.database.Table")
    @mock.patch("common.common.get_table_name")
    def test_query_generates_correctly_with_no_optional_parameters(
        self, get_table_name_mock, table_mock
    ):
        table_name = "test-table"
        table_mock.return_value = [table_name]
        get_table_name_mock.return_value = table_name
        args = {"table-name": table_name}
        expected = f"SELECT * FROM {table_name}"
        actual = query.build_query(args)

        self.assertEqual(expected, actual)

    @mock.patch("common.database.Table")
    @mock.patch("common.common.get_table_name")
    def test_query_generates_correctly_with_one_optional_parameter(
        self, get_table_name_mock, table_mock
    ):
        table_name = "test-table"
        table_mock.return_value = [table_name]
        get_table_name_mock.return_value = table_name
        args = {"hbase-id-like": "test", "table-name": table_name}
        expected = f"SELECT * FROM {table_name} WHERE hbase_id LIKE 'test'"
        actual = query.build_query(args)

        self.assertEqual(expected, actual)

    @mock.patch("common.database.Table")
    @mock.patch("common.common.get_table_name")
    def test_query_generates_correctly_with_two_optional_parameters(
        self, get_table_name_mock, table_mock
    ):
        table_name = "test-table"
        table_mock.return_value = [table_name]
        get_table_name_mock.return_value = table_name
        args = {
            "hbase-id-like": "test",
            "correlation-id-equals": "test2",
            "table-name": table_name,
        }
        expected = f"SELECT * FROM {table_name} WHERE hbase_id LIKE 'test' AND correlation_id = 'test2'"
        actual = query.build_query(args)

        self.assertEqual(expected, actual)

    @mock.patch("common.database.Table")
    @mock.patch("common.common.get_table_name")
    def test_query_generates_correctly_with_two_optional_parameters_and_ignored_other_parameters(
        self, get_table_name_mock, table_mock
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
        expected = f"SELECT * FROM {table_name} WHERE hbase_id LIKE 'test' AND correlation_id = 'test2'"
        actual = query.build_query(args)

        self.assertEqual(expected, actual)

    @mock.patch("common.database.Table")
    @mock.patch("common.common.get_table_name")
    def test_query_generates_correctly_with_two_optional_parameters_of_different_type(
        self, get_table_name_mock, table_mock
    ):
        table_name = "test-table"
        table_mock.return_value = [table_name]
        get_table_name_mock.return_value = table_name
        args = {
            "hbase-id-like": "test",
            "kafka-partition-equals": "1",
            "table-name": table_name,
        }
        expected = f"SELECT * FROM {table_name} WHERE hbase_id LIKE 'test' AND kafka_partition = 1"
        actual = query.build_query(args)

        self.assertEqual(expected, actual)

    @mock.patch("common.database.Table")
    @mock.patch("common.common.get_table_name")
    def test_query_generates_correctly_with_two_optional_parameters_using_or_comparison_method(
        self, get_table_name_mock, table_mock
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
        expected = f"SELECT * FROM {table_name} WHERE hbase_id LIKE 'test' OR kafka_partition = 1"
        actual = query.build_query(args)

        self.assertEqual(expected, actual)

    @mock.patch("common.database.Table")
    @mock.patch("common.common.get_table_name")
    def test_query_generates_correctly_with_three_optional_parameters(
        self, get_table_name_mock, table_mock
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
        expected = f"SELECT * FROM {table_name} WHERE hbase_id LIKE 'test' AND correlation_id = 'test2' AND kafka_partition = 1"
        actual = query.build_query(args)

        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()