# ClickHouse Cluster

`export VERSION=22.12; docker-compose up -d`

`python run.py`


```
sudo apt update && sudo apt upgrade -y

curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

sudo groupadd docker
sudo usermod -aG docker ${USER}
newgrp docker

sudo curl -SL https://github.com/docker/compose/releases/download/v2.14.2/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
sudo chmod +x /usr/bin/docker-compose

git clone https://github.com/DerekChia/clickhouse-docker-cluster

cd clickhouse-docker-cluster

python3 generate.py 
```

# Experiments (TODO)
1. embedded 3x CHK with CH nodes
2. separate CH Keeper to 3 nodes
3. with 3x CHK, increase number of CH nodes until CHK cannot keep up
3.1 increase CHK vertically (RAM and CPU)
3.2 increase number of metadata (increase tables, parts, partitions, DDLs)
3.3 tuning CHK config: operation_timeout_ms and session_timeout_ms
4. Do step 3 with ZK

https://clickhouse.com/docs/en/operations/settings/merge-tree-settings/#always_fetch_merged_part

# Notes
- embedded keeper is enabled on first replica in shard by default