-- create table
CREATE TABLE test ON CLUSTER 'default' 
(
	key UInt32, 
	value1 String, 
	value2 String, 
	value3 String
) 
ENGINE=ReplicatedMergeTree('/clickhouse/{shard}/{uuid}/test', '{replica}') 
ORDER BY key 
PARTITION BY (key % 2);

-- insert
INSERT INTO test SELECT * FROM generateRandom('key UInt32, value1 String, value2 String, value3 String') LIMIT 200_000_000;

-- drop
DROP TABLE test ON CLUSTER '{cluster}';