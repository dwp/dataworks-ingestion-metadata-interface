DROP FUNCTION IF EXISTS column_exists;
CREATE FUNCTION column_exists(table_name_param VARCHAR(256), column_name_param VARCHAR(256)) RETURNS BOOLEAN
BEGIN
    DECLARE result INT;
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = table_name_param AND COLUMN_NAME = column_name_param INTO result;
    RETURN result != 0;
END;

DROP PROCEDURE IF EXISTS add_index;
CREATE PROCEDURE add_index(IN table_name_param VARCHAR(256), IN column_name_param VARCHAR(256))
BEGIN
    DECLARE column_exists BOOLEAN;
    SET column_exists = column_exists(table_name_param, column_name_param);
    IF column_exists THEN
        SET @add_index_ddl = concat('CREATE INDEX ', column_name_param, ' on ', table_name_param, ' (', column_name_param, ')');
        PREPARE add_index_ddl from @add_index_ddl;
        EXECUTE add_index_ddl;
        DEALLOCATE PREPARE add_index_ddl;
    END IF;
END;

DROP PROCEDURE IF EXISTS add_column;
CREATE PROCEDURE add_column(IN table_name_param VARCHAR(256), IN column_name_param VARCHAR(256), IN column_spec VARCHAR(256))
BEGIN
    DECLARE column_exists BOOLEAN;
    SET column_exists = column_exists(table_name_param, column_name_param);
    IF !column_exists THEN
        SET @alter_table_ddl = concat('ALTER TABLE ', table_name_param,  ' ADD COLUMN ', column_name_param, ' ', column_spec);
        PREPARE alter_table_ddl from @alter_table_ddl;
        EXECUTE alter_table_ddl;
        DEALLOCATE PREPARE alter_table_ddl;
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

DROP PROCEDURE IF EXISTS alter_reconciliation_table;
CREATE PROCEDURE alter_reconciliation_table(IN table_name_param VARCHAR(256))
BEGIN
    CALL add_indexed_column(table_name_param, 'last_checked_timestamp', 'DATETIME NULL');
END;
