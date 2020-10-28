Feature: The alter table stored procedure adds, removes columns and partitions as necessary

  Scenario Outline: Table has required number of partitions
    Given the <table_name> table is created with <initial_partition_count> partitions
    Then the <table_name> table will have <initial_partition_count> partitions
    When the <table_name> table is populated with <row_count> rows
    Then the <table_name> table will have <row_count> rows
    When the <table_name> table is altered to have <required_partition_count> partitions
    Then the <table_name> table will have the last_checked_timestamp column
    And the <table_name> table will have the last_checked_timestamp index
    And the <table_name> table will have <required_partition_count> partitions
    And the <table_name> table will have <row_count> rows
    Examples:
      | table_name | initial_partition_count | required_partition_count | row_count |
      | ucfs       |                       1 |                        1 |       100 |
      | ucfs       |                       1 |                       10 |       100 |
      | ucfs       |                      10 |                       10 |       100 |
      | ucfs       |                      10 |                       15 |       100 |
      | ucfs       |                      15 |                       10 |       100 |
      | ucfs       |                      20 |                        1 |       100 |
