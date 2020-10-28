Feature: The alter table stored procedure adds, removes columns and partitions as necessary

  Scenario Outline: Table has required number of partitions
    Given the <table_name> table is created with <initial_partition_count> partitions
    Then the <table_name> table will have <initial_partition_count> partitions
    When the <table_name> table is populated with 100 rows
    Then the <table_name> table will have 100 rows
    When the <table_name> table is altered to have <required_partition_count> partitions
    Then the <table_name> table will have the last_checked_timestamp column
    And the <table_name> table will have the last_checked_timestamp index
    And the <table_name> table will have <required_partition_count> partitions
    And the <table_name> table will have 100 rows
    Examples:
      |table_name |initial_partition_count | required_partition_count |
      | ucfs      | 1                      | 10                       |
      | ucfs      | 10                     | 10                       |
      | ucfs      | 10                     | 15                       |
      | ucfs      | 15                     | 10                       |
      | ucfs      | 20                     |  1                       |
