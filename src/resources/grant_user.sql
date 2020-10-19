CREATE USER IF NOT EXISTS k2hbwriter;
CREATE USER IF NOT EXISTS reconciler;
CREATE USER IF NOT EXISTS datareader;
CREATE USER IF NOT EXISTS hbasewriter;

GRANT SELECT, INSERT ON `{table_name}` to k2hbwriter;
GRANT SELECT, INSERT, UPDATE (reconciled_result, reconciled_timestamp) ON `{table_name}` to reconciler;
GRANT SELECT ON `{table_name}` to datareader;
GRANT SELECT, INSERT ON `{table_name}` to hbasewriter;
