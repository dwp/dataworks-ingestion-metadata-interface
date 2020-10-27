#!/usr/bin/env python3

import json
import pytest
import unittest
from unittest import mock
from common import database
from unittest.mock import MagicMock, call


class TestDatabase(unittest.TestCase):
    @mock.patch("query_lambda.query.logger")
    def test_query_generates_correctly_with_no_optional_parameters(self, logger_mock):
        expected = {
            "test_row1_column2": {"t": "test_row1_column1", "t": "test_row1_column2"},
            "test_row2_column2": {"t": "test_row2_column1", "t": "test_row2_column2"},
            "test_row3_column2": {"t": "test_row3_column1", "t": "test_row3_column2"},
        }

        cursor_mock = MagicMock()
        cursor_mock.description = [("test_column_name1"), ("test_column_name2")]
        cursor_mock.fetchall.return_value = (
            ("test_row1_column1", "test_row1_column2"),
            ("test_row2_column1", "test_row2_column2"),
            ("test_row3_column1", "test_row3_column2"),
        )

        connection_mock = MagicMock()
        connection_mock.cursor.return_value = cursor_mock

        actual = database.execute_query_to_dict("some test sql", connection_mock)

        connection_mock.commit.assert_called_once()

        self.maxDiff = None
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
