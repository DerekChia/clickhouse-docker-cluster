# ClickHouse Cluster Automation

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
- embedded 3x CHK with CH nodes
- separate CH Keeper to 3 nodes
- increase number of CH nodes until CHK cannot keep up, then increase CHK vertically (RAM and CPU)
- increase tables, parts, partitions, DDLs
- increase operation_timeout_ms and session_timeout_ms