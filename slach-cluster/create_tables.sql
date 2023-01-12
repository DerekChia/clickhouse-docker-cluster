DROP DATABASE IF EXISTS keeper_bench SYNC;
CREATE DATABASE keeper_bench;
CREATE TABLE keeper_bench.keeper_bench (p UInt64, x UInt64)
    ENGINE=ReplicatedSummingMergeTree('/clickhouse/tables/{database}/{table}', '{replica}' )
    ORDER BY tuple()
    PARTITION BY p
    SETTINGS in_memory_parts_enable_wal=0,
        min_bytes_for_wide_part=104857600,
        min_bytes_for_compact_part=10485760,
        parts_to_delay_insert=1000000,
        parts_to_throw_insert=1000000,
        max_parts_in_total=1000000;
