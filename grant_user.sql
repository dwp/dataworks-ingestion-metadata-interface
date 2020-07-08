CREATE USER IF NOT EXISTS `k2hbwriter`;
CREATE USER IF NOT EXISTS `reconciler`;
CREATE USER IF NOT EXISTS `reader`;

GRANT SELECT, INSERT ON `%(table_name)s` to `k2hbwriter`;
GRANT SELECT (*), UPDATE (reconciled_result, reconciled_timestamp) ON `%(table_name)s` to `reconciler`;
GRANT SELECT ON `%(table_name)s` to `reader`;