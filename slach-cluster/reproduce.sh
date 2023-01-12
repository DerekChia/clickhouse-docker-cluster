#!/usr/bin/env bash
truncate -s 0 ./*.log
docker-compose -f docker-compose-keeper-3-nodes.yaml pull
docker-compose -f docker-compose-keeper-3-nodes.yaml down --remove-orphans
docker-compose -f docker-compose-keeper-3-nodes.yaml up -d clickhouse
sleep 7
cat ./create_tables.sql | docker-compose -f docker-compose-keeper-3-nodes.yaml exec -T clickhouse clickhouse-client --echo --progress -mn --time
cat ./keeper_bench.sql | docker-compose -f docker-compose-keeper-3-nodes.yaml exec -T clickhouse clickhouse-client --echo --progress -mn --time
cat ./drop_tables.sql | docker-compose -f docker-compose-keeper-3-nodes.yaml exec -T clickhouse clickhouse-client --echo --progress -mn --time
docker-compose -f docker-compose-keeper-3-nodes.yaml down --remove-orphans

# 
docker-compose -f docker-compose-keeper.yaml pull
docker-compose -f docker-compose-keeper.yaml down --remove-orphans
docker-compose -f docker-compose-keeper.yaml up -d clickhouse
sleep 7
cat ./create_tables.sql | docker-compose -f docker-compose-keeper-3-nodes.yaml exec -T clickhouse clickhouse-client --echo --progress -mn --time
cat ./keeper_bench.sql | docker-compose -f docker-compose-keeper.yaml exec -T clickhouse clickhouse-client --echo --progress -mn --time
cat ./drop_tables.sql | docker-compose -f docker-compose-keeper-3-nodes.yaml exec -T clickhouse clickhouse-client --echo --progress -mn --time
docker-compose -f docker-compose-keeper.yaml down --remove-orphans

#
docker-compose -f docker-compose-zookeeper.yaml pull
docker-compose -f docker-compose-zookeeper.yaml down --remove-orphans
docker-compose -f docker-compose-zookeeper.yaml up -d clickhouse
sleep 7
cat ./create_tables.sql | docker-compose -f docker-compose-keeper-3-nodes.yaml exec -T clickhouse clickhouse-client --echo --progress -mn --time
cat ./keeper_bench.sql | docker-compose -f docker-compose-zookeeper.yaml exec -T clickhouse clickhouse-client --echo --progress -mn --time
cat ./drop_tables.sql | docker-compose -f docker-compose-keeper-3-nodes.yaml exec -T clickhouse clickhouse-client --echo --progress -mn --time
docker-compose -f docker-compose-zookeeper.yaml down --remove-orphans