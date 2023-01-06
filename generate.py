import shutil
import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# general
version = "22.12"
shards = 1
replicas = 3
num_keepers = 3

# resources for each node
cpus = 8.0
mem_limit = "8192m"

cluster_name = f"cluster_{shards}S_{replicas}R"
context = {
    "hostnames": [],
    "server_ids": [],
    "shards": [],
    "replicas": [],
    "native_protocol_ports": [],
    "http_api_ports": [],
    "keeper_ports": [],
}
internal_replication = True

native_protocol_port = 9000
http_api_port = 8123
keeper_port = 9181

node_count = 0
for shard in range(1, shards + 1):
    for replica in range(1, replicas + 1):
        node_count += 1
        context["hostnames"].append(f"chnode{node_count}")
        context["server_ids"].append(f"{node_count}")
        context["shards"].append(f"{shard}")
        context["replicas"].append(f"{replica}")
        context["native_protocol_ports"].append(f"{native_protocol_port}")
        context["http_api_ports"].append(f"{http_api_port}")
        context["keeper_ports"].append(f"{keeper_port}")
        native_protocol_port += 1
        http_api_port += 1
        keeper_port += 1

# print(context)
# print(cluster_name)


def _delete_cluster_generated(cluster_generated_name):
    path = Path(cluster_generated_name)
    if path.is_dir():
        shutil.rmtree(path)


def create_cluster_generated(cluster_generated_name):
    _delete_cluster_generated(cluster_generated_name)
    Path(cluster_generated_name).mkdir(parents=True, exist_ok=True)
    Path(f"{cluster_generated_name}/configs").mkdir(parents=True, exist_ok=True)


def generate_docker_compose():
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("docker-compose.txt")

    filename = f"cluster/docker-compose.yml"
    content = template.render(context, version=version, cpus=cpus, mem_limit=mem_limit)
    with open(filename, mode="w", encoding="utf-8") as f:
        f.write(content)


def generate_config(context):
    environment = Environment(loader=FileSystemLoader(f"templates/configs/"))

    # create configs directory
    for hostname in context["hostnames"]:
        Path(f"cluster/configs/{hostname}").mkdir(parents=True, exist_ok=True)

    # docker_related_config.xml
    filename = f"templates/configs/docker_related_config.xml"
    for hostname in context["hostnames"]:
        filename_generated = f"cluster/configs/{hostname}/docker_related_config.xml"
        shutil.copyfile(filename, filename_generated)

    # keeper_enable.xml
    template = environment.get_template("keeper_enable.txt")

    for count in range(len(context["hostnames"])):
        if count < num_keepers:
            hostname = context["hostnames"][count]
            server_id = context["server_ids"][count]

            filename_generated = f"cluster/configs/{hostname}/keeper_enable.xml"
            content = template.render(
                context, server_id=server_id, num_keepers=num_keepers
            )
            with open(filename_generated, mode="w", encoding="utf-8") as f:
                f.write(content)

    # keeper_use.xml
    template = environment.get_template("keeper_use.txt")

    for count in range(len(context["hostnames"])):
        hostname = context["hostnames"][count]
        server_id = context["server_ids"][count]

        filename_generated = f"cluster/configs/{hostname}/keeper_use.xml"
        content = template.render(context, num_keepers=num_keepers)
        with open(filename_generated, mode="w", encoding="utf-8") as f:
            f.write(content)

    # macros.xml
    template = environment.get_template("macros.txt")

    for count in range(len(context["hostnames"])):
        hostname = context["hostnames"][count]
        shard = context["shards"][count]
        replica = context["replicas"][count]

        filename_generated = f"cluster/configs/{hostname}/macros.xml"
        content = template.render(
            cluster_name=cluster_name, shard=shard, replica=replica
        )
        with open(filename_generated, mode="w", encoding="utf-8") as f:
            f.write(content)

    # remote_servers.xml
    template = environment.get_template("remote_servers.txt")

    for count in range(len(context["hostnames"])):
        hostname = context["hostnames"][count]
        shard = context["shards"][count]
        replica = context["replicas"][count]

        filename_generated = f"cluster/configs/{hostname}/remote_servers.xml"
        content = template.render(
            context,
            cluster_name=cluster_name,
            internal_replication=internal_replication,
            num_shard=shards,
            num_replica=replicas,
        )
        with open(filename_generated, mode="w", encoding="utf-8") as f:
            f.write(content)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()

    # parser.add_argument(
    #     "-v",
    #     "--version",
    #     type=float,
    #     default=22.12,
    #     required=True,
    #     help="ClickHouse version",
    # )
    # parser.add_argument(
    #     "-s", "--shards", type=int, default=1, required=True, help="Number of shards"
    # )
    # parser.add_argument(
    #     "-r",
    #     "--replicas",
    #     type=int,
    #     default=1,
    #     required=True,
    #     help="Number of replicas",
    # )
    # parser.add_argument(
    #     "-k",
    #     "--num_keepers",
    #     type=int,
    #     default=3,
    #     required=True,
    #     help="Number of Keepers (Min. 3)",
    # )

    # parser.add_argument("--cpus", type=int, default=1, help="CPUs for each node")
    # parser.add_argument(
    #     "--memory", type=int, default=8192, help="RAM (mb) for each node"
    # )

    # parser.add_argument("-d", "--directory", type=str, default="cluster")

    # args = parser.parse_args()

    # print(f"{args}")

    create_cluster_generated("cluster")
    generate_docker_compose()
    generate_config(context)
