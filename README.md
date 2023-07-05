# ClickHouse Cluster Generator

**Note: This is still WIP**

ClickHouse Cluster Generator is a tiny script that generates a docker-compose yaml file based on a different number of input parameters. With this, you can programmatically setup different number of ClickHouse and Keeper nodes, that is readily configured with Prometheus, Grafana dashboards and cAdvisor.

## Getting Started
To get started, create a Python environment and install the only dependency which is `jinja2`. 

```
cd clickhouse-cluster-generator
python -m venv venv
source venv/bin/activate
pip install -r requirements
```

Next, generate the cluster based on your specifically. The parameters below will generate a cluster with 1 shard, 3 replicas and with 3 ClickHouse Keeper. 
```
python generate.py --cluster-directory cluster_1 --shard 1 --replica 3 --keeper-count 3 --ch-version 23.5 --keeper-mode chkeeper

docker-compose -f cluster_1/docker-compose.yml down && docker-compose -f cluster_1/docker-compose.yml up
```

If you have orphan containers that are leftover by previous cluster, you can remove all of them using the following command
```
docker container prune -f 
```

## List of ports
Ports within the containers are mapped to the localhost with the following configuration.

ClickHouse Native Port
- localhost:29000 is mapped to chnode1:9000
- localhost:29001 is mapped to chnode2:9000

ClickHouse HTTP Port
- localhost:28123 is mapped to chnode1:8123
- localhost:28124 is mapped to chnode2:8123

ClickHouse Keeper 
- localhost:12181 is mapped to chkeeper1:2181
- localhost:12182 is mapped to chkeeper2:2182

Prometheus
- localhost:9090 is mapped to prometheus:9090

Grafana
- localhost:3000 is mapped to grafana:3000

cAdvisor
- localhost:8081 is mapped to cadvisor8080

