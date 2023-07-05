DROP DATABASE IF EXISTS db ON CLUSTER 'default' SYNC;
CREATE DATABASE db ON CLUSTER 'default';

DROP TABLE IF EXISTS db.tbl ON CLUSTER 'default' SYNC;
CREATE TABLE db.tbl ON CLUSTER 'default' 
    (p UInt64, x UInt64) 
    ENGINE=ReplicatedSummingMergeTree
    ORDER BY tuple()
    PARTITION BY p
    -- SETTINGS in_memory_parts_enable_wal=0,
    --     min_bytes_for_wide_part=104857600,
    --     min_bytes_for_compact_part=10485760,
    --     parts_to_delay_insert=1000000,
    --     parts_to_throw_insert=1000000,
    --     max_parts_in_total=1000000;