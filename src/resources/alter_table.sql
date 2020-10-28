DROP FUNCTION IF EXISTS column_exists;
CREATE FUNCTION column_exists(table_name_param VARCHAR(256), column_name_param VARCHAR(256)) RETURNS BOOLEAN
BEGIN
    DECLARE result INT;
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = table_name_param AND COLUMN_NAME = column_name_param INTO result;
    RETURN result != 0;
END;

DROP FUNCTION IF EXISTS index_exists;
CREATE FUNCTION index_exists(table_name_param VARCHAR(256), index_name_param VARCHAR(256)) RETURNS BOOLEAN
BEGIN
    DECLARE result INT;
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.STATISTICS
    WHERE table_name = table_name_param and index_name = index_name_param INTO result;
    RETURN result != 0;
END;

DROP PROCEDURE IF EXISTS execute_ddl;
CREATE PROCEDURE execute_ddl(IN ddl VARCHAR(512))
BEGIN
    SET @ddl_statement = ddl;
    PREPARE ddl_statement from @ddl_statement;
    EXECUTE ddl_statement;
    DEALLOCATE PREPARE ddl_statement;
END;

DROP PROCEDURE IF EXISTS add_index;
CREATE PROCEDURE add_index(IN table_name_param VARCHAR(256), IN column_name_param VARCHAR(256))
BEGIN
    DECLARE column_exists BOOLEAN;
    DECLARE index_exists BOOLEAN;

    SET column_exists = column_exists(table_name_param, column_name_param);
    IF column_exists THEN
        SET index_exists = index_exists(table_name_param, column_name_param);
        IF !index_exists THEN
            CALL execute_ddl(concat('CREATE INDEX ', column_name_param, ' on ', table_name_param, ' (', column_name_param, ')'));
        END IF;
    END IF;
END;

DROP PROCEDURE IF EXISTS add_column;
CREATE PROCEDURE add_column(IN table_name_param VARCHAR(256), IN column_name_param VARCHAR(256), IN column_spec VARCHAR(256))
BEGIN
    DECLARE column_exists BOOLEAN;
    SET column_exists = column_exists(table_name_param, column_name_param);
    IF !column_exists THEN
        CALL execute_ddl(concat('ALTER TABLE ', table_name_param,  ' ADD COLUMN ', column_name_param, ' ', column_spec));
    END IF;
END;

DROP PROCEDURE IF EXISTS add_indexed_column;
CREATE PROCEDURE add_indexed_column(IN table_name_param VARCHAR(256), IN column_name_param VARCHAR(256), IN column_spec VARCHAR(256))
BEGIN
    DECLARE column_exists BOOLEAN;
    SET column_exists = column_exists(table_name_param, column_name_param);
    IF !column_exists THEN
        CALL add_column(table_name_param, column_name_param, column_spec);
        CALL add_index(table_name_param, column_name_param);
    END IF;
END;

DROP PROCEDURE IF EXISTS partition_table;
CREATE PROCEDURE partition_table(IN table_name_param VARCHAR(256), IN required_partition_count INTEGER)
BEGIN
    DECLARE existing_partition_count INTEGER;
    DECLARE partition_difference INTEGER;

    SELECT COUNT(*) FROM INFORMATION_SCHEMA.PARTITIONS WHERE TABLE_NAME = table_name_param INTO existing_partition_count;
    IF existing_partition_count <> required_partition_count THEN
        IF existing_partition_count < 2 THEN
            IF required_partition_count > 1 THEN
                CALL execute_ddl(concat('ALTER TABLE ', table_name_param,  ' PARTITION BY HASH(id) PARTITIONS ', required_partition_count));
            END IF;
        ELSE
            SET partition_difference = required_partition_count - existing_partition_count;
            IF partition_difference > 0 THEN
                CALL execute_ddl(concat('ALTER TABLE ', table_name_param,  ' ADD PARTITION PARTITIONS ', partition_difference));
            ELSE
                IF required_partition_count > 1 THEN
                    CALL execute_ddl(concat('ALTER TABLE ', table_name_param,  ' COALESCE PARTITION ', abs(partition_difference)));
                ELSE
                    CALL execute_ddl(concat('ALTER TABLE ', table_name_param,  ' REMOVE PARTITIONING'));
                END IF;
            END IF;
        END IF;
    END IF;
END;

DROP PROCEDURE IF EXISTS alter_reconciliation_table;
CREATE PROCEDURE alter_reconciliation_table(IN table_name_param VARCHAR(256), IN partition_count INT)
BEGIN
    CALL add_indexed_column(table_name_param, 'last_checked_timestamp', 'DATETIME NULL');
    CALL partition_table(table_name_param, partition_count);
END;
