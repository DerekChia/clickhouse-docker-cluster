#!/usr/bin/env bash
docker-compose -f ./cluster/docker-compose.yml down --remove-orphans
docker-compose -f ./cluster/docker-compose.yml up -d 
sleep 7
cat ./tests/0001_create_insert_drop/create_table.sql | docker-compose -f ./cluster/docker-compose.yml exec -T chnode_with_chkeeper1 clickhouse-client -mn --time
cat ./tests/0001_create_insert_drop/insert_rows.sql | docker-compose -f ./cluster/docker-compose.yml exec -T chnode_with_chkeeper1 clickhouse-client -mn --time
cat ./tests/0001_create_insert_drop/drop_table.sql | docker-compose -f ./cluster/docker-compose.yml exec -T chnode_with_chkeeper1 clickhouse-client -mn --time


cat ./tests/0002_test/test.sql | docker-compose -f ./cluster/docker-compose.yml exec -T chnode_with_chkeeper1 clickhouse-client -mn --time
