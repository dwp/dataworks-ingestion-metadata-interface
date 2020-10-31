from behave import given, when, then

from utility.database import Database
from utility.serverless import LambdaUtility

database_utility = Database()
lambda_utility = LambdaUtility()


@given("the {table_name} table is created with {partition_count} partitions and {row_count} rows")
def step_impl(context, table_name, partition_count, row_count):
    database_utility.drop_table(table_name)
    database_utility.create_table(table_name, int(partition_count))
    database_utility.populate_table(table_name, int(row_count))


@then("the {table_name} table will have {row_count} rows")
def step_impl(context, table_name, row_count):
    actual = database_utility.row_count(table_name)
    assert actual == int(row_count)


@when("the {table_name} table is altered to have {partition_count} partitions")
def step_impl(context, table_name, partition_count):
    lambda_utility.alter_table(table_name, int(partition_count))


@then("the {table_name} table will have the {column_name} column")
def step_impl(context, table_name, column_name):
    count = database_utility.column_count(table_name, column_name)
    assert count == 1


@then("the {table_name} table will have the {index_name} index")
def step_impl(context, table_name, index_name):
    count = database_utility.index_count(table_name, index_name)
    assert count == 1


@then("the {table_name} table will have {partition_count} partitions")
def step_impl(context, table_name, partition_count):
    actual = database_utility.partition_count(table_name)
    assert actual == int(partition_count)
