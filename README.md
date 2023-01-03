# ClickHouse Cluster Automation

`export VERSION=22.12; docker-compose up -d`

`python run.py`

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