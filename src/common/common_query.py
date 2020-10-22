def get_queryable_options(args, queryable_fields):
    queryable_options = []
    for queryable_field in queryable_fields:
        if queryable_field[1] in args:
            field_name = queryable_field[0]
            value_to_check = args[queryable_field[1]]
            comparison_operator = queryable_field[2]
            field_type = queryable_field[3]
            if comparison_operator.upper() == "LIKE":
                value_to_check = f"%{value_to_check}%"
            if field_type in ["string"]:
                value_to_check = f"'{value_to_check}'"
            queryable_options.append(
                f"{field_name} {comparison_operator} {value_to_check}"
            )
    return queryable_options

def get_queryable_fields():
    return [
        ["hbase_id", "hbase-id-equals", "=", "string"],
        ["hbase_id", "hbase-id-like", "LIKE", "string"],
        ["hbase_timestamp", "hbase-timestamp-equals", "=", "int"],
        ["correlation_id", "correlation-id-equals", "=", "string"],
        ["topic_name", "topic-name-equals", "=", "string"],
        ["kafka_partition", "kafka-partition-equals", "=", "int"],
        ["kafka_offset", "kafka-offset-equals", "=", "int"],
        ["reconciled_result", "reconciled-result-equals", "=", "int"],
    ]
