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
def test_generate_docker_compose_yaml():
    args = argparse.Namespace(**config_dict)

    c = cluster.Cluster(args)
    c.prepare()
    c.generate_obj()
    c.generate_docker_compose()
    c.generate_config()
    c._delete_cluster_directory()

def test_generate_and_start_docker_compose_cluster():
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
    http_api_port_end = args.http_api_port + 20_000 + (args.replica * args.shard)

    for port in range(http_api_port_start, http_api_port_end):
        client = clickhouse_connect.get_client(host='localhost', port=port, username='default', password='')
        result = client.query('select 1;')
        assert result.result_rows == [(1,)]

    subprocess.run(['docker', 'compose', '-f', f'{args.cluster_directory}/docker-compose.yml' , 'down', '-v'])

    c._delete_cluster_directory()

