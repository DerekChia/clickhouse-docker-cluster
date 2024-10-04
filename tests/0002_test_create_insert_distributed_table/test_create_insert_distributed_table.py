# test_example.py
import time
import subprocess
import argparse
import yaml
from pathlib import Path
from app import cluster
import clickhouse_connect

with open(Path(__file__).resolve().parent / 'config.yaml') as stream:
    try:
        config_dict = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# @pytest.fixture
def test_create_insert_distributed_table():
    args = argparse.Namespace(**config_dict)

    c = cluster.Cluster(args)
    c.prepare()
    c.generate_obj()
    c.generate_docker_compose()
    c.generate_config()

    subprocess.run(['docker', 'compose', '-f', f'{args.cluster_directory}/docker-compose.yml' , 'down', '-v'])
    subprocess.run(['docker', 'compose', '-f', f'{args.cluster_directory}/docker-compose.yml' , 'up', '-d'])

    time.sleep(3)

    http_api_port_start = args.http_api_port + 20_000

    s1r1 = clickhouse_connect.get_client(host='localhost', port=http_api_port_start, username='default', password='')
    s1r2 = clickhouse_connect.get_client(host='localhost', port=http_api_port_start+1, username='default', password='')
    s2r1 = clickhouse_connect.get_client(host='localhost', port=http_api_port_start+2, username='default', password='')
    s2r2 = clickhouse_connect.get_client(host='localhost', port=http_api_port_start+2, username='default', password='') 

    # CREATE TABLE
    s1r1.query('create table tbl_dist on cluster `default` (col1 UInt64, col2 UInt64) engine=Distributed(default, default, tbl, rand());')    
    s1r1.query('create table tbl on cluster `default` (col1 UInt64, col2 UInt64) engine = ReplicatedMergeTree() order by col1;')
    
    # tables we have
    res = s2r1.query("select hostname() hn, table from clusterAllReplicas(default, system.tables) where database = 'default' group by all order by hn;")
    result = sorted(res.result_set)

    node_names = [args.chnode_prefix + str(node_count) for node_count in range(1, args.shard * args.replica + 1)]
    
    # tables we expect
    expected = []
    for created_table in ['tbl', 'tbl_dist']:
        for node_name in node_names:
            expected.append((node_name, created_table))
    expected = sorted(expected)

    # check
    assert set(result).intersection(set(expected)) == set(result)

    # INSERT
    s1r1.query('insert into tbl_dist select rand(0), rand(1) from system.numbers limit 1_000 settings distributed_foreground_insert = 1;')
    time.sleep(3)
    s2r1.query('insert into tbl_dist select rand(0), rand(1) from system.numbers limit 1_000 settings distributed_foreground_insert = 1;')
    time.sleep(3)

    res = s1r1.query('select count() from tbl_dist;')

    # check
    assert res.result_rows[0][0] == 2000

    # check replication
    s1r1_result = s1r1.query('select count() from tbl;')
    s1r2_result = s1r2.query('select count() from tbl;')

    assert s1r1_result.result_rows == s1r2_result.result_rows

    s2r1_result = s2r1.query('select count() from tbl;')
    s2r2_result = s2r2.query('select count() from tbl;')

    assert s2r1_result.result_rows == s2r2_result.result_rows

    subprocess.run(['docker', 'compose', '-f', f'{args.cluster_directory}/docker-compose.yml' , 'down', '-v'])

    c._delete_cluster_directory()
