# ClickHouse Cluster

## Getting Started
```
python generate.py \
    --version 22.11 \
    --shard 2 \
    --replica 4 \
    --keeper-mode embedded \
    --keeper-count 3
```

## TODO
- Issue `select 1` to confirm chnode aliveness
- Issue `ruok` to standalone keeper to check aliveness

## Experiments (TODO)
1. embedded 3x CHK with CH nodes
2. separate CH Keeper to 3 nodes
3. with 3x CHK, increase number of CH nodes until CHK cannot keep up
3.1 increase CHK vertically (RAM and CPU)
3.2 increase number of metadata (increase tables, parts, partitions, DDLs)
3.3 tuning CHK config: operation_timeout_ms and session_timeout_ms
4. Do step 3 with ZK

https://clickhouse.com/docs/en/operations/settings/merge-tree-settings/#always_fetch_merged_part

