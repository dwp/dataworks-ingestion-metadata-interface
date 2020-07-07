CREATE TABLE `%(table_name)s` (
    `id` INT NOT NULL,
    `hbase_id` VARCHAR(45) NULL,
    `hbase_timestamp` DATETIME NULL,
    `write_timestamp` DATETIME NULL,
    `correlation_id` VARCHAR(45) NULL,
    `topic_name` VARCHAR(45) NULL,
    `kafka_partition` INT NULL,
    `kafka_offset` INT NULL,
    `reconciled_result` TINYINT NOT NULL DEFAULT 1,
    `reconciled_timestamp` DATETIME NULL,
    PRIMARY KEY (`id`)
);
